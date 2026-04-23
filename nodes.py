import json
import logging
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

import events
from prompts import (
    ANALYST_SYSTEM,
    BUILDER_SYSTEM,
    DESIGNER_SYSTEM,
    SCRIPTER_SYSTEM,
    SEARCHER_SYSTEM,
    WRITER_SYSTEM,
)
from state import ResearchState
from tools import RESEARCH_TOOLS
from video import (
    ScriptOut,
    build_video_agent,
    copy_styles_snapshot,
    init_project,
    run_lint,
    run_render,
    run_transcribe,
    run_tts,
    slugify,
)

log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

_searcher = None


def _llm(max_tokens: int = 8192, temperature: float = 0.4) -> ChatAnthropic:
    return ChatAnthropic(model=MODEL, max_tokens=max_tokens, temperature=temperature)


def _message_text(msg) -> str:
    content = getattr(msg, "content", msg)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and "text" in block:
                    parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


def _get_searcher():
    global _searcher
    if _searcher is None:
        _searcher = create_react_agent(
            _llm(max_tokens=8192), RESEARCH_TOOLS, prompt=SEARCHER_SYSTEM
        )
        log.info("Initialized searcher with tools: %s", [t.name for t in RESEARCH_TOOLS])
    return _searcher


class _stage:
    """Context manager: emit stage_start on enter; on an unhandled exception,
    emit stage_end with status=error. Success-path stage_end is emitted
    explicitly by the node body so it can attach artifact metadata."""

    def __init__(self, stage: str):
        self.stage = stage
        self._tok = None

    def __enter__(self):
        events.emit("stage_start", stage=self.stage)
        self._tok = events.set_stage(self.stage)
        return self

    def __exit__(self, exc_type, exc, tb):
        events.reset_stage(self._tok)
        if exc is not None:
            events.emit(
                "stage_end",
                stage=self.stage,
                status="error",
                error=f"{exc_type.__name__}: {exc}",
            )
        return False


def _save_report_artifact(run_id: str | None, report: str) -> str | None:
    if not run_id:
        return None
    path = events.EVENTS_DIR / f"{run_id}.report.md"
    try:
        path.write_text(report, encoding="utf-8")
    except OSError:
        return None
    return str(path)


async def searcher_node(state: ResearchState) -> dict:
    log.info("searcher_node: researching topic %r", state["topic"])
    with _stage("searcher"):
        agent = _get_searcher()
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=f"Research topic: {state['topic']}")]},
            config={"callbacks": [events.LangChainEventCallback("searcher")]},
        )
        messages = result["messages"]
        findings = _message_text(messages[-1])
        events.emit(
            "stage_end",
            stage="searcher",
            status="ok",
            artifacts={"research_findings_chars": len(findings)},
        )
    return {"search_messages": messages, "research_findings": findings}


async def analyst_node(state: ResearchState) -> dict:
    log.info("analyst_node: synthesizing findings")
    with _stage("analyst"):
        findings = state.get("research_findings", "")
        resp = await _llm().ainvoke(
            [
                SystemMessage(content=ANALYST_SYSTEM),
                HumanMessage(content=f"Researcher findings:\n\n{findings}"),
            ]
        )
        analysis = _message_text(resp)
        events.emit(
            "stage_end",
            stage="analyst",
            status="ok",
            artifacts={"analysis_chars": len(analysis)},
        )
    return {"analysis": analysis}


async def writer_node(state: ResearchState) -> dict:
    log.info("writer_node: drafting report")
    with _stage("writer"):
        analysis = state.get("analysis", "")
        resp = await _llm(max_tokens=8192).ainvoke(
            [
                SystemMessage(content=WRITER_SYSTEM),
                HumanMessage(content=f"Analyst summary:\n\n{analysis}"),
            ]
        )
        report = _message_text(resp)
        _save_report_artifact(events.current_run_id(), report)
        events.emit(
            "stage_end",
            stage="writer",
            status="ok",
            artifacts={"report": "report.md", "report_chars": len(report)},
        )
    return {"report": report}


# ---------------------------------------------------------------------------
# Video pipeline — deep agents with filesystem access to /skills/
# ---------------------------------------------------------------------------


async def scripter_node(state: ResearchState) -> dict:
    log.info("scripter_node: drafting narration (deep agent)")
    with _stage("scripter"):
        agent = build_video_agent(
            system_prompt=SCRIPTER_SYSTEM,
            response_format=ScriptOut,
        )
        result = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            f"Topic: {state.get('topic', '')}\n\n"
                            f"Report to condense into a 20–35 second narration:\n\n"
                            f"{state.get('report', '')}\n\n"
                            "Return a ScriptOut with fields title, slug, script."
                        )
                    )
                ]
            },
            config={"callbacks": [events.LangChainEventCallback("scripter")]},
        )
        structured: ScriptOut = result["structured_response"]
        slug = slugify(structured.slug or structured.title or state.get("topic", ""))
        events.emit(
            "stage_end",
            stage="scripter",
            status="ok",
            artifacts={
                "title": structured.title,
                "slug": slug,
                "script_chars": len(structured.script),
            },
        )
    return {
        "script": structured.script,
        "title": structured.title,
        "slug": slug,
    }


async def narrator_node(state: ResearchState) -> dict:
    log.info("narrator_node: scaffolding project + TTS + transcribe")
    with _stage("narrator"):
        slug = state["slug"]
        script = state["script"]
        project_dir = await init_project(slug, stage="narrator")
        audio_path = await run_tts(project_dir, script, stage="narrator")
        _, words = await run_transcribe(project_dir, audio_path, stage="narrator")
        log.info("narrator_node: %d words transcribed", len(words))
        events.emit(
            "stage_end",
            stage="narrator",
            status="ok",
            artifacts={
                "project_dir": str(project_dir),
                "audio_path": str(audio_path),
                "word_count": len(words),
            },
        )
    return {
        "project_dir": str(project_dir),
        "audio_path": str(audio_path),
        "transcript": words,
    }


def _project_relpath(project_dir: Path) -> str:
    """Path of the project dir relative to the repo root, with a leading slash
    so it matches the virtual-mode FilesystemBackend's rules."""
    from video import REPO_ROOT

    rel = project_dir.resolve().relative_to(REPO_ROOT)
    return "/" + str(rel).replace("\\", "/")


async def designer_node(state: ResearchState) -> dict:
    log.info("designer_node: authoring DESIGN.md (deep agent)")
    with _stage("designer"):
        project_dir = Path(state["project_dir"])
        project_rel = _project_relpath(project_dir)
        design_path_virtual = f"{project_rel}/DESIGN.md"

        agent = build_video_agent(
            system_prompt=DESIGNER_SYSTEM,
            project_relpath=project_rel,
        )
        await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            f"Topic: {state.get('topic', '')}\n"
                            f"Video title: {state.get('title', '')}\n"
                            f"Slug: {state.get('slug', '')}\n"
                            f"Canvas: 1080x1920 portrait (9:16)\n\n"
                            f"Narration script:\n{state.get('script', '')}\n\n"
                            f"Source report (for tonal grounding):\n"
                            f"{state.get('report', '')}\n\n"
                            f"=== YOUR TASK ===\n"
                            f"Browse the HyperFrames skill docs under /skills/ as needed, "
                            f"then author the full DESIGN.md and write it to:\n"
                            f"  {design_path_virtual}\n"
                            f"Use your write_file tool. The file is the only deliverable."
                        )
                    )
                ]
            },
            config={"callbacks": [events.LangChainEventCallback("designer")]},
        )

        design_file = project_dir / "DESIGN.md"
        if not design_file.is_file():
            raise RuntimeError(
                f"designer did not write {design_file}. "
                f"Check the agent trace for filesystem-tool errors."
            )
        design_md = design_file.read_text(encoding="utf-8")
        events.emit(
            "stage_end",
            stage="designer",
            status="ok",
            artifacts={"design_brief": "DESIGN.md", "design_chars": len(design_md)},
        )
    return {"design_brief": design_md}


async def builder_node(state: ResearchState) -> dict:
    log.info("builder_node: authoring index.html (deep agent)")
    with _stage("builder"):
        project_dir = Path(state["project_dir"])
        project_rel = _project_relpath(project_dir)
        index_path_virtual = f"{project_rel}/index.html"

        audio_path = Path(state["audio_path"])
        audio_filename = audio_path.name
        words = state.get("transcript", [])
        spoken_end = max((w.get("end", 0.0) for w in words), default=0.0)
        total_duration = max(spoken_end + 3.0, 6.0)

        agent = build_video_agent(
            system_prompt=BUILDER_SYSTEM,
            project_relpath=project_rel,
        )
        await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            f"Topic: {state.get('topic', '')}\n"
                            f"Video title: {state.get('title', '')}\n"
                            f"Canvas: 1080x1920 portrait (9:16)\n"
                            f"Audio filename (in project root): {audio_filename}\n"
                            f"Narration spoken length: {spoken_end:.2f}s\n"
                            f"Target composition duration: {total_duration:.2f}s "
                            f"(narration + {total_duration - spoken_end:.2f}s "
                            f"Instagram follow overlay)\n\n"
                            f"=== DESIGN.md (authoritative visual direction) ===\n"
                            f"{state.get('design_brief', '')}\n\n"
                            f"=== Narration script ===\n{state.get('script', '')}\n\n"
                            f"=== Word-level transcript (JSON, seconds) ===\n"
                            f"{json.dumps(words, indent=2)}\n\n"
                            f"=== YOUR TASK ===\n"
                            f"Browse the HyperFrames skill docs under /skills/ as needed, "
                            f"then author the full index.html and write it to:\n"
                            f"  {index_path_virtual}\n"
                            f"Use your write_file tool. The file is the only deliverable."
                        )
                    )
                ]
            },
            config={"callbacks": [events.LangChainEventCallback("builder")]},
        )

        index_file = project_dir / "index.html"
        if not index_file.is_file():
            raise RuntimeError(
                f"builder did not write {index_file}. "
                f"Check the agent trace for filesystem-tool errors."
            )
        html = index_file.read_text(encoding="utf-8")
        events.emit(
            "stage_end",
            stage="builder",
            status="ok",
            artifacts={"html": "index.html", "html_chars": len(html)},
        )
    return {"html": html}


async def renderer_node(state: ResearchState) -> dict:
    log.info("renderer_node: lint + render")
    with _stage("renderer"):
        project_dir = Path(state["project_dir"])
        slug = state["slug"]
        lint_findings = await run_lint(project_dir, stage="renderer")
        video_path = await run_render(project_dir, stage="renderer")
        copy_styles_snapshot(project_dir, slug)
        log.info("renderer_node: video at %s", video_path)
        events.emit(
            "stage_end",
            stage="renderer",
            status="ok",
            artifacts={
                "video_path": str(video_path),
                "lint_errors": (lint_findings or {}).get("errorCount"),
                "lint_warnings": (lint_findings or {}).get("warningCount"),
            },
        )
    return {"video_path": str(video_path)}
