"""Helpers for the HyperFrames video pipeline.

Pure Python glue — no HyperFrames rules, no styling. The video-generation
agents are LangChain deep agents created here; they get read-only filesystem
access to the full `skills/` tree (so any skill file is reachable on demand,
not a pre-selected bundle) and read/write access scoped to their per-run
project directory. This module also wraps the `npx hyperframes` subprocesses
and provides the Pydantic shapes the scripter returns.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import FilesystemBackend
from pydantic import BaseModel, Field

import events

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_ROOT = REPO_ROOT / "skills"
VIDEOS_ROOT = REPO_ROOT / "outputs" / "videos"
STYLES_ROOT = REPO_ROOT / "styles"

DEEP_AGENT_MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Pydantic models used by LLM nodes
# ---------------------------------------------------------------------------


class ScriptOut(BaseModel):
    title: str = Field(..., description="Punchy 3–6 word video title.")
    slug: str = Field(..., description="Filesystem-safe, lowercase-hyphenated slug.")
    script: str = Field(..., description="Narration text, 20–35 seconds when spoken.")


# ---------------------------------------------------------------------------
# Slugs and paths
# ---------------------------------------------------------------------------

_SLUG_CLEAN = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Lowercase, hyphenated, ASCII-only slug — safe for filesystems and CLI."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = _SLUG_CLEAN.sub("-", normalized.lower()).strip("-")
    return slug or "video"


def project_path(slug: str) -> Path:
    return VIDEOS_ROOT / slug


# ---------------------------------------------------------------------------
# Deep agents for video generation
# ---------------------------------------------------------------------------


_SKILLS_READ_PATHS = [
    # The repo exposes skills/ as symlinks to .agents/skills/; agents may use
    # either path since FilesystemBackend canonicalizes through symlinks.
    "/skills/**",
    "/.agents/skills/**",
]


def _repo_backend() -> FilesystemBackend:
    """Virtual filesystem rooted at the repo. Symlinks under `skills/` resolve
    into `.agents/skills/` which still lies inside the repo, so the whole
    HyperFrames documentation tree is reachable."""
    return FilesystemBackend(root_dir=str(REPO_ROOT), virtual_mode=True)


def _permissions_for(project_relpath: str) -> list[FilesystemPermission]:
    """Permission stack for a video-gen agent.

    Rules apply first-match-wins. Agent may:
      - read + write inside its own per-run project dir
      - read anything under /skills/ (and its canonical /.agents/skills/)
      - NOT write anywhere else
    """
    project_glob = f"{project_relpath.rstrip('/')}/**"
    return [
        FilesystemPermission(operations=["read", "write"], paths=[project_glob]),
        FilesystemPermission(operations=["read"], paths=_SKILLS_READ_PATHS),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ]


def build_video_agent(
    *,
    system_prompt: str,
    project_relpath: str | None = None,
    response_format: type[BaseModel] | None = None,
) -> Any:
    """Create a deep agent pre-wired with filesystem access appropriate for
    the video pipeline.

    Args:
      system_prompt: the role-specific prompt; the agent also inherits the
        built-in deep-agent system prompt (planning + filesystem tool usage).
      project_relpath: e.g. "/outputs/videos/<slug>" — grants read+write on
        that subtree. Omit for read-only agents (like the scripter).
      response_format: optional Pydantic model for structured responses.
    """
    if project_relpath:
        perms = _permissions_for(project_relpath)
    else:
        perms = [
            FilesystemPermission(operations=["read"], paths=_SKILLS_READ_PATHS),
            FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
        ]
    return create_deep_agent(
        model=DEEP_AGENT_MODEL,
        system_prompt=system_prompt,
        backend=_repo_backend(),
        permissions=perms,
        response_format=response_format,
    )


# ---------------------------------------------------------------------------
# Subprocess helpers (all async)
# ---------------------------------------------------------------------------


async def _run(
    *args: str,
    cwd: Path | None = None,
    check: bool = True,
    stage: str | None = None,
) -> tuple[int, str, str]:
    """Run a command, return (returncode, stdout, stderr). Raise on non-zero
    when `check=True`. If `stage` is set, stream each stdout/stderr line to
    the event bus as a `subprocess_line` event so the UI can display it live."""
    log.info("run: %s (cwd=%s)", " ".join(args), cwd)
    if stage:
        events.emit("subprocess_line", stage=stage, stream="cmd", line=" ".join(args))
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    if not stage:
        stdout_b, stderr_b = await proc.communicate()
        stdout = stdout_b.decode(errors="replace")
        stderr = stderr_b.decode(errors="replace")
    else:
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        async def _pump(reader, stream_name: str, sink: list[str]) -> None:
            while True:
                line_b = await reader.readline()
                if not line_b:
                    break
                line = line_b.decode(errors="replace").rstrip("\n")
                sink.append(line)
                events.emit("subprocess_line", stage=stage, stream=stream_name, line=line)

        await asyncio.gather(
            _pump(proc.stdout, "stdout", stdout_lines),
            _pump(proc.stderr, "stderr", stderr_lines),
        )
        await proc.wait()
        stdout = "\n".join(stdout_lines)
        stderr = "\n".join(stderr_lines)

    if check and proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(args)}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    return proc.returncode or 0, stdout, stderr


def _parse_json_line(stdout: str) -> dict | None:
    """Find the last JSON object in stdout (CLI prints it when --json is set)."""
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


async def init_project(slug: str, stage: str | None = None) -> Path:
    """Scaffold a per-run HyperFrames project at outputs/videos/<slug>.

    If the directory already exists, it's wiped first so re-runs start clean.
    """
    VIDEOS_ROOT.mkdir(parents=True, exist_ok=True)
    target = project_path(slug)
    if target.exists():
        shutil.rmtree(target)

    await _run(
        "npx",
        "hyperframes",
        "init",
        slug,
        "--non-interactive",
        "--skip-skills",
        "--skip-transcribe",
        cwd=VIDEOS_ROOT,
        stage=stage,
    )
    if not target.is_dir():
        raise RuntimeError(f"hyperframes init did not produce {target}")
    log.info("initialized project at %s", target)
    return target


async def run_tts(
    project_dir: Path, script_text: str, voice: str = "af_nova", stage: str | None = None
) -> Path:
    """Write `script.txt` and generate `narration.wav` via `hyperframes tts`."""
    script_path = project_dir / "script.txt"
    script_path.write_text(script_text, encoding="utf-8")
    audio_path = project_dir / "narration.wav"
    _, stdout, _ = await _run(
        "npx",
        "hyperframes",
        "tts",
        str(script_path),
        "--voice",
        voice,
        "--output",
        str(audio_path),
        "--json",
        cwd=project_dir,
        stage=stage,
    )
    payload = _parse_json_line(stdout) or {}
    out = payload.get("outputPath")
    if out:
        audio_path = Path(out)
    if not audio_path.is_file():
        raise RuntimeError(f"tts did not produce audio at {audio_path}")
    return audio_path


async def run_transcribe(
    project_dir: Path, audio_path: Path, model: str = "small.en", stage: str | None = None
) -> tuple[Path, list[dict]]:
    """Transcribe `audio_path` to word-level JSON and return (path, words)."""
    _, stdout, _ = await _run(
        "npx",
        "hyperframes",
        "transcribe",
        str(audio_path),
        "--model",
        model,
        "--json",
        cwd=project_dir,
        stage=stage,
    )
    payload = _parse_json_line(stdout) or {}
    transcript_path = Path(payload.get("transcriptPath") or project_dir / "transcript.json")
    if not transcript_path.is_file():
        raise RuntimeError(f"transcribe did not produce {transcript_path}")
    words = json.loads(transcript_path.read_text(encoding="utf-8"))
    if not isinstance(words, list):
        raise RuntimeError(f"unexpected transcript shape in {transcript_path}")
    return transcript_path, words


async def run_lint(project_dir: Path, stage: str | None = None) -> dict | None:
    """Run `hyperframes lint --json` and return the parsed findings.

    Does not raise on warnings. Callers that want to fail on errors should
    check the return value.
    """
    _, stdout, stderr = await _run(
        "npx",
        "hyperframes",
        "lint",
        "--json",
        cwd=project_dir,
        check=False,
        stage=stage,
    )
    payload = _parse_json_line(stdout)
    if payload is None and stderr:
        log.warning("lint stderr: %s", stderr.strip()[:500])
    if payload:
        log.info(
            "lint: %s errors, %s warnings",
            payload.get("errorCount", "?"),
            payload.get("warningCount", "?"),
        )
    return payload


async def run_render(project_dir: Path, quality: str = "standard", stage: str | None = None) -> Path:
    """Render the composition to MP4. Returns the output path."""
    _, stdout, _ = await _run(
        "npx",
        "hyperframes",
        "render",
        "--quality",
        quality,
        cwd=project_dir,
        stage=stage,
    )
    match = re.search(r"([^\s]+\.mp4)\b", stdout)
    if match:
        candidate = Path(match.group(1))
        if not candidate.is_absolute():
            candidate = project_dir / candidate
        if candidate.is_file():
            return candidate
    renders_dir = project_dir / "renders"
    if renders_dir.is_dir():
        mp4s = sorted(renders_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
        if mp4s:
            return mp4s[-1]
    raise RuntimeError(f"render did not produce an mp4 under {project_dir}")


# ---------------------------------------------------------------------------
# Styles reference snapshot
# ---------------------------------------------------------------------------


def copy_styles_snapshot(project_dir: Path, slug: str) -> Path:
    """Copy DESIGN.md and index.html from the rendered project into
    styles/<slug>/ so the generated style guide survives past the render."""
    dest = STYLES_ROOT / slug
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("DESIGN.md", "index.html"):
        src = project_dir / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    return dest
