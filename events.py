"""Pipeline observability event bus.

Writes one JSON object per line to outputs/events/<run_id>.jsonl.
A separate FastAPI server tails the file and broadcasts events to the UI
over SSE. All emit() calls are no-ops when no run is active, so the CLI
keeps working with or without a server listening.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
EVENTS_DIR = REPO_ROOT / "outputs" / "events"
LATEST_FILE = EVENTS_DIR / "latest.txt"

_state: dict[str, Any] = {
    "run_id": None,
    "path": None,
}
_lock = threading.Lock()
_stage_ctx: ContextVar[str | None] = ContextVar("events_stage", default=None)


def start_run(topic: str, mode: str) -> str:
    """Begin a new run. Returns its run_id."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    path = EVENTS_DIR / f"{run_id}.jsonl"
    with _lock:
        _state["run_id"] = run_id
        _state["path"] = path
    LATEST_FILE.write_text(run_id, encoding="utf-8")
    emit("run_start", topic=topic, mode=mode, run_id=run_id)
    return run_id


def end_run(status: str = "ok", error: str | None = None) -> None:
    emit("run_end", status=status, error=error)
    with _lock:
        _state["run_id"] = None
        _state["path"] = None


def current_run_id() -> str | None:
    return _state["run_id"]


def set_stage(stage: str | None):
    """Return a context token so the caller can reset. Used by nodes to
    tag unrelated log messages with the currently running stage."""
    return _stage_ctx.set(stage)


def reset_stage(token) -> None:
    _stage_ctx.reset(token)


def _preview(value: Any, limit: int = 400) -> Any:
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + f"… (+{len(value) - limit} chars)"
    if isinstance(value, (list, tuple, dict)):
        try:
            s = json.dumps(value, default=str)
        except Exception:
            s = str(value)
        return s if len(s) <= limit else s[:limit] + "…"
    return value


def emit(event_type: str, stage: str | None = None, **data: Any) -> None:
    """Append one event line. No-op when no run is active."""
    path: Path | None
    with _lock:
        path = _state["path"]
    if path is None:
        return
    if stage is None:
        stage = _stage_ctx.get()
    record = {
        "ts": time.time(),
        "type": event_type,
        "stage": stage,
        **data,
    }
    try:
        line = json.dumps(record, default=str, ensure_ascii=False)
    except Exception:
        line = json.dumps(
            {"ts": record["ts"], "type": event_type, "stage": stage, "error": "serialize-failed"}
        )
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Python logging bridge
# ---------------------------------------------------------------------------


class EventLogHandler(logging.Handler):
    """Forward every log record to the event bus as a `log` event."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
        except Exception:
            msg = record.msg if isinstance(record.msg, str) else repr(record.msg)
        emit(
            "log",
            level=record.levelname,
            logger=record.name,
            msg=msg,
        )


# ---------------------------------------------------------------------------
# LangChain callback bridge
# ---------------------------------------------------------------------------


def _lazy_callback_base():
    from langchain_core.callbacks import AsyncCallbackHandler

    return AsyncCallbackHandler


def LangChainEventCallback(stage: str):
    """Factory (not a class) — lazy-imports the langchain base class so
    `events.py` has no hard dependency on langchain at module load time."""

    Base = _lazy_callback_base()

    class _Cb(Base):
        def __init__(self) -> None:
            super().__init__()
            self.stage = stage
            self._tool_t0: dict[str, float] = {}

        async def on_tool_start(self, serialized, input_str, *, run_id=None, **kwargs):
            name = (serialized or {}).get("name") or "tool"
            key = str(run_id) if run_id else name
            self._tool_t0[key] = time.time()
            emit(
                "tool_call",
                stage=self.stage,
                tool=name,
                args=_preview(input_str),
            )

        async def on_tool_end(self, output, *, run_id=None, **kwargs):
            key = str(run_id) if run_id else ""
            t0 = self._tool_t0.pop(key, None)
            elapsed = time.time() - t0 if t0 else None
            emit(
                "tool_result",
                stage=self.stage,
                result=_preview(str(output), 300),
                elapsed=elapsed,
            )

        async def on_tool_error(self, error, *, run_id=None, **kwargs):
            emit(
                "tool_error",
                stage=self.stage,
                error=_preview(str(error), 300),
            )

    return _Cb()
