"""FastAPI observability server.

Tails outputs/events/<run_id>.jsonl and streams events to the browser
via SSE. Also serves the UI and the artifacts each pipeline stage writes.

Launch: `python server.py`  (default http://127.0.0.1:8000)
"""

from __future__ import annotations

import asyncio
import json
import mimetypes
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

REPO_ROOT = Path(__file__).resolve().parent
EVENTS_DIR = REPO_ROOT / "outputs" / "events"
LATEST_FILE = EVENTS_DIR / "latest.txt"
VIDEOS_DIR = REPO_ROOT / "outputs" / "videos"
UI_DIR = REPO_ROOT / "ui"

# Artifacts the UI is allowed to fetch from a project dir.
ARTIFACT_WHITELIST = {
    "report.md",
    "script.txt",
    "DESIGN.md",
    "index.html",
    "transcript.json",
    "narration.wav",
}

app = FastAPI(title="Pipeline Observer")
app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


def _event_path(run_id: str) -> Path:
    # run_id is user-controllable via URL; reject path traversal.
    if "/" in run_id or ".." in run_id or "\\" in run_id:
        raise HTTPException(status_code=400, detail="bad run_id")
    p = EVENTS_DIR / f"{run_id}.jsonl"
    if not p.is_file():
        raise HTTPException(status_code=404, detail="run not found")
    return p


def _parse_first_and_last(path: Path) -> tuple[dict | None, dict | None]:
    first = last = None
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if first is None:
                    first = obj
                last = obj
    except FileNotFoundError:
        return None, None
    return first, last


@app.get("/api/runs")
def list_runs() -> JSONResponse:
    if not EVENTS_DIR.is_dir():
        return JSONResponse([])
    rows = []
    for p in sorted(EVENTS_DIR.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True):
        first, last = _parse_first_and_last(p)
        if not first:
            continue
        rows.append(
            {
                "run_id": p.stem,
                "topic": first.get("topic"),
                "mode": first.get("mode"),
                "started_at": first.get("ts"),
                "ended_at": last.get("ts") if last and last.get("type") == "run_end" else None,
                "status": last.get("status") if last and last.get("type") == "run_end" else "running",
            }
        )
    return JSONResponse(rows)


@app.get("/api/runs/latest")
def latest_run() -> JSONResponse:
    if not LATEST_FILE.is_file():
        raise HTTPException(status_code=404, detail="no runs yet")
    run_id = LATEST_FILE.read_text(encoding="utf-8").strip()
    if not run_id:
        raise HTTPException(status_code=404, detail="empty latest")
    return JSONResponse({"run_id": run_id})


async def _tail_events(path: Path) -> AsyncIterator[bytes]:
    """Yield Server-Sent-Event chunks until a `run_end` event is seen and
    we've reached EOF. Reconnects are the client's job via EventSource."""
    f = path.open("r", encoding="utf-8")
    try:
        ended = False
        buffer = ""
        yield b": connected\n\n"
        while True:
            chunk = f.read()
            if chunk:
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    # SSE needs literal `data: <line>\n\n`
                    yield f"data: {line}\n\n".encode("utf-8")
                    # Peek at event type to know when to stop tailing.
                    try:
                        obj = json.loads(line)
                        if obj.get("type") == "run_end":
                            ended = True
                    except json.JSONDecodeError:
                        pass
            else:
                if ended:
                    # File fully drained and run is over — close the stream.
                    return
                # keep-alive ping every few seconds so proxies don't drop us
                await asyncio.sleep(0.3)
                yield b": keepalive\n\n"
                await asyncio.sleep(0.3)
    finally:
        f.close()


@app.get("/api/runs/{run_id}/events")
async def stream_events(run_id: str) -> StreamingResponse:
    path = _event_path(run_id)
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(_tail_events(path), media_type="text/event-stream", headers=headers)


def _extract_slug(run_id: str) -> str | None:
    """Read the run's first few events to find the slug the scripter chose."""
    path = _event_path(run_id)
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "stage_end" and obj.get("stage") == "scripter":
                    slug = (obj.get("artifacts") or {}).get("slug")
                    if slug:
                        return slug
                # narrator also reports slug/project_dir
                if obj.get("type") == "stage_end" and obj.get("stage") == "narrator":
                    pd = (obj.get("artifacts") or {}).get("project_dir")
                    if pd:
                        return Path(pd).name
    except FileNotFoundError:
        return None
    return None


@app.get("/api/runs/{run_id}/artifact/{name}")
def get_artifact(run_id: str, name: str) -> Response:
    if name not in ARTIFACT_WHITELIST and name != "video" and not name.startswith("report"):
        raise HTTPException(status_code=400, detail="artifact not allowed")

    # report.md is stored under outputs/events/<run_id>.report.md (writer writes it there)
    if name == "report.md":
        candidate = EVENTS_DIR / f"{run_id}.report.md"
        if candidate.is_file():
            return FileResponse(candidate, media_type="text/markdown")

    slug = _extract_slug(run_id)
    if not slug:
        raise HTTPException(status_code=404, detail="no project dir yet")
    project_dir = VIDEOS_DIR / slug
    if not project_dir.is_dir():
        raise HTTPException(status_code=404, detail="project dir missing")

    if name == "video":
        renders = project_dir / "renders"
        if renders.is_dir():
            mp4s = sorted(renders.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
            if mp4s:
                return FileResponse(mp4s[-1], media_type="video/mp4")
        raise HTTPException(status_code=404, detail="no rendered mp4")

    target = project_dir / name
    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"{name} not found")

    mt, _ = mimetypes.guess_type(target.name)
    if name.endswith(".md"):
        mt = "text/markdown; charset=utf-8"
    elif name.endswith(".html"):
        # Force plain-text so the browser shows source, not rendered HTML.
        mt = "text/plain; charset=utf-8"
    elif name.endswith(".json"):
        mt = "application/json; charset=utf-8"
    elif name.endswith(".txt"):
        mt = "text/plain; charset=utf-8"
    return FileResponse(target, media_type=mt or "application/octet-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
