"""Helpers for the HyperFrames video pipeline.

Pure Python glue — no HyperFrames rules, no styling. Agents read the skill
markdown via `load_skill_context` and inject it into their own prompts; this
module only wires subprocess calls to `npx hyperframes {init,tts,transcribe,
lint,render}` and provides the Pydantic shapes the LLM nodes use.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
import unicodedata
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_ROOT = REPO_ROOT / "skills"
VIDEOS_ROOT = REPO_ROOT / "outputs" / "videos"
STYLES_ROOT = REPO_ROOT / "styles"


# ---------------------------------------------------------------------------
# Skill context bundles
# ---------------------------------------------------------------------------

# Logical agent → list of skill files (paths relative to `skills/`).
# The files are read verbatim and concatenated into a single markdown blob
# that gets substituted into the `{HF_CONTEXT}` placeholder in a prompt.
SKILL_BUNDLES: dict[str, list[str]] = {
    "designer": [
        "hyperframes/SKILL.md",
        "hyperframes/visual-styles.md",
        "hyperframes/house-style.md",
        "hyperframes-registry/SKILL.md",
    ],
    "builder": [
        "hyperframes/SKILL.md",
        "hyperframes/references/captions.md",
        "hyperframes/references/transitions.md",
        "hyperframes/references/motion-principles.md",
        "gsap/SKILL.md",
        "hyperframes-registry/SKILL.md",
    ],
}


@lru_cache(maxsize=None)
def load_skill_context(bundle: str) -> str:
    """Read the skill files for a named bundle and concatenate them.

    Missing files are logged and skipped — the rest of the bundle still loads.
    """
    paths = SKILL_BUNDLES.get(bundle)
    if not paths:
        raise ValueError(f"unknown skill bundle: {bundle!r}")
    chunks: list[str] = []
    for rel in paths:
        full = SKILLS_ROOT / rel
        if not full.is_file():
            log.warning("skill file missing: %s", full)
            continue
        text = full.read_text(encoding="utf-8")
        chunks.append(f"\n\n---\n# skills/{rel}\n\n{text}")
    return "".join(chunks).strip()


# ---------------------------------------------------------------------------
# Pydantic models used by LLM nodes
# ---------------------------------------------------------------------------


class ScriptOut(BaseModel):
    title: str = Field(..., description="Punchy 3–6 word video title.")
    slug: str = Field(..., description="Filesystem-safe, lowercase-hyphenated slug.")
    script: str = Field(..., description="Narration text, 20–35 seconds when spoken.")


class DesignOut(BaseModel):
    design_md: str = Field(
        ...,
        description="Full DESIGN.md content following the Visual Identity Gate.",
    )


class HTMLOut(BaseModel):
    html: str = Field(..., description="Complete HyperFrames index.html document.")


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
# Subprocess helpers (all async)
# ---------------------------------------------------------------------------


async def _run(
    *args: str,
    cwd: Path | None = None,
    check: bool = True,
) -> tuple[int, str, str]:
    """Run a command, return (returncode, stdout, stderr). Raise on non-zero
    when `check=True`."""
    log.info("run: %s (cwd=%s)", " ".join(args), cwd)
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_b, stderr_b = await proc.communicate()
    stdout = stdout_b.decode(errors="replace")
    stderr = stderr_b.decode(errors="replace")
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


async def init_project(slug: str) -> Path:
    """Scaffold a per-run HyperFrames project at outputs/videos/<slug>.

    If the directory already exists, it's wiped first so re-runs start clean.
    """
    VIDEOS_ROOT.mkdir(parents=True, exist_ok=True)
    target = project_path(slug)
    if target.exists():
        shutil.rmtree(target)

    # `init` always creates the named directory under cwd.
    await _run(
        "npx",
        "hyperframes",
        "init",
        slug,
        "--non-interactive",
        "--skip-skills",
        "--skip-transcribe",
        cwd=VIDEOS_ROOT,
    )
    if not target.is_dir():
        raise RuntimeError(f"hyperframes init did not produce {target}")
    log.info("initialized project at %s", target)
    return target


async def run_tts(
    project_dir: Path, script_text: str, voice: str = "af_nova"
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
    )
    payload = _parse_json_line(stdout) or {}
    out = payload.get("outputPath")
    if out:
        audio_path = Path(out)
    if not audio_path.is_file():
        raise RuntimeError(f"tts did not produce audio at {audio_path}")
    return audio_path


async def run_transcribe(
    project_dir: Path, audio_path: Path, model: str = "small.en"
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
    )
    payload = _parse_json_line(stdout) or {}
    transcript_path = Path(payload.get("transcriptPath") or project_dir / "transcript.json")
    if not transcript_path.is_file():
        raise RuntimeError(f"transcribe did not produce {transcript_path}")
    words = json.loads(transcript_path.read_text(encoding="utf-8"))
    if not isinstance(words, list):
        raise RuntimeError(f"unexpected transcript shape in {transcript_path}")
    return transcript_path, words


async def run_lint(project_dir: Path) -> dict | None:
    """Run `hyperframes lint --json` and return the parsed findings.

    Does not raise on warnings. Callers that want to fail on errors should
    check the return value.
    """
    rc, stdout, stderr = await _run(
        "npx",
        "hyperframes",
        "lint",
        "--json",
        cwd=project_dir,
        check=False,
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


async def run_render(project_dir: Path, quality: str = "standard") -> Path:
    """Render the composition to MP4. Returns the output path."""
    _, stdout, _ = await _run(
        "npx",
        "hyperframes",
        "render",
        "--quality",
        quality,
        cwd=project_dir,
    )
    # The CLI logs the output path; if we can't parse it, fall back to the
    # newest file in renders/.
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
