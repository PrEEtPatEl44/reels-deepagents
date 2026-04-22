import json
import logging
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

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

# Singleton so we don't rebuild the ReAct agent on every graph step.
_searcher = None


def _llm(max_tokens: int = 8192, temperature: float = 0.4) -> ChatAnthropic:
    return ChatAnthropic(model=MODEL, max_tokens=max_tokens, temperature=temperature)


def _message_text(msg) -> str:
    """Extract plain text from a LangChain message whose content may be a list of content blocks."""
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


async def searcher_node(state: ResearchState) -> dict:
    log.info("searcher_node: researching topic %r", state["topic"])
    agent = _get_searcher()
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=f"Research topic: {state['topic']}")]}
    )
    messages = result["messages"]
    findings = _message_text(messages[-1])
    return {"search_messages": messages, "research_findings": findings}


async def analyst_node(state: ResearchState) -> dict:
    log.info("analyst_node: synthesizing findings")
    findings = state.get("research_findings", "")
    resp = await _llm().ainvoke(
        [
            SystemMessage(content=ANALYST_SYSTEM),
            HumanMessage(content=f"Researcher findings:\n\n{findings}"),
        ]
    )
    return {"analysis": _message_text(resp)}


async def writer_node(state: ResearchState) -> dict:
    log.info("writer_node: drafting report")
    analysis = state.get("analysis", "")
    resp = await _llm(max_tokens=8192).ainvoke(
        [
            SystemMessage(content=WRITER_SYSTEM),
            HumanMessage(content=f"Analyst summary:\n\n{analysis}"),
        ]
    )
    return {"report": _message_text(resp)}


# ---------------------------------------------------------------------------
# Video pipeline — deep agents with filesystem access to /skills/
# ---------------------------------------------------------------------------


async def scripter_node(state: ResearchState) -> dict:
    log.info("scripter_node: drafting narration (deep agent)")
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
        }
    )
    structured: ScriptOut = result["structured_response"]
    slug = slugify(structured.slug or structured.title or state.get("topic", ""))
    return {
        "script": structured.script,
        "title": structured.title,
        "slug": slug,
    }


async def narrator_node(state: ResearchState) -> dict:
    log.info("narrator_node: scaffolding project + TTS + transcribe")
    slug = state["slug"]
    script = state["script"]
    project_dir = await init_project(slug)
    audio_path = await run_tts(project_dir, script)
    _, words = await run_transcribe(project_dir, audio_path)
    log.info("narrator_node: %d words transcribed", len(words))
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
        }
    )

    design_file = project_dir / "DESIGN.md"
    if not design_file.is_file():
        raise RuntimeError(
            f"designer did not write {design_file}. "
            f"Check the agent trace for filesystem-tool errors."
        )
    design_md = design_file.read_text(encoding="utf-8")
    return {"design_brief": design_md}


async def builder_node(state: ResearchState) -> dict:
    log.info("builder_node: authoring index.html (deep agent)")
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
        }
    )

    index_file = project_dir / "index.html"
    if not index_file.is_file():
        raise RuntimeError(
            f"builder did not write {index_file}. "
            f"Check the agent trace for filesystem-tool errors."
        )
    html = index_file.read_text(encoding="utf-8")
    return {"html": html}


async def renderer_node(state: ResearchState) -> dict:
    log.info("renderer_node: lint + render")
    project_dir = Path(state["project_dir"])
    slug = state["slug"]
    await run_lint(project_dir)
    video_path = await run_render(project_dir)
    copy_styles_snapshot(project_dir, slug)
    log.info("renderer_node: video at %s", video_path)
    return {"video_path": str(video_path)}
