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
    DesignOut,
    HTMLOut,
    ScriptOut,
    copy_styles_snapshot,
    init_project,
    load_skill_context,
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
# Video pipeline
# ---------------------------------------------------------------------------


async def scripter_node(state: ResearchState) -> dict:
    log.info("scripter_node: drafting narration")
    report = state.get("report", "")
    topic = state.get("topic", "")
    scripter = _llm(max_tokens=2048, temperature=0.6).with_structured_output(ScriptOut)
    result: ScriptOut = await scripter.ainvoke(
        [
            SystemMessage(content=SCRIPTER_SYSTEM),
            HumanMessage(
                content=(
                    f"Topic: {topic}\n\n"
                    f"Report to condense into a 20-35 second narration:\n\n{report}"
                )
            ),
        ]
    )
    slug = slugify(result.slug or result.title or topic)
    return {"script": result.script, "title": result.title, "slug": slug}


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


async def designer_node(state: ResearchState) -> dict:
    log.info("designer_node: authoring DESIGN.md")
    project_dir = Path(state["project_dir"])
    context = load_skill_context("designer")
    system = DESIGNER_SYSTEM.replace("{HF_CONTEXT}", context)
    designer = _llm(max_tokens=8192, temperature=0.7).with_structured_output(DesignOut)
    result: DesignOut = await designer.ainvoke(
        [
            SystemMessage(content=system),
            HumanMessage(
                content=(
                    f"Topic: {state.get('topic', '')}\n"
                    f"Video title: {state.get('title', '')}\n\n"
                    f"Narration script:\n{state.get('script', '')}\n\n"
                    f"Source report (for tonal grounding):\n{state.get('report', '')}"
                )
            ),
        ]
    )
    design_path = project_dir / "DESIGN.md"
    design_path.write_text(result.design_md, encoding="utf-8")
    return {"design_brief": result.design_md}


async def builder_node(state: ResearchState) -> dict:
    log.info("builder_node: authoring index.html")
    project_dir = Path(state["project_dir"])
    context = load_skill_context("builder")
    system = BUILDER_SYSTEM.replace("{HF_CONTEXT}", context)

    audio_path = Path(state["audio_path"])
    audio_filename = audio_path.name
    words = state.get("transcript", [])
    # Narration duration drives composition duration; add 3s tail for the
    # Instagram follow overlay per the prompt contract.
    spoken_end = max((w.get("end", 0.0) for w in words), default=0.0)
    total_duration = max(spoken_end + 3.0, 6.0)

    builder = _llm(max_tokens=16000, temperature=0.5).with_structured_output(HTMLOut)
    result: HTMLOut = await builder.ainvoke(
        [
            SystemMessage(content=system),
            HumanMessage(
                content=(
                    f"Topic: {state.get('topic', '')}\n"
                    f"Video title: {state.get('title', '')}\n"
                    f"Canvas: 1080x1920 portrait (9:16)\n"
                    f"Audio filename (in project root): {audio_filename}\n"
                    f"Narration spoken length: {spoken_end:.2f}s\n"
                    f"Target composition duration: {total_duration:.2f}s "
                    f"(narration + {total_duration - spoken_end:.2f}s Instagram follow overlay)\n\n"
                    f"=== DESIGN.md (authoritative visual direction) ===\n"
                    f"{state.get('design_brief', '')}\n\n"
                    f"=== Narration script ===\n{state.get('script', '')}\n\n"
                    f"=== Word-level transcript (JSON, seconds) ===\n"
                    f"{json.dumps(words, indent=2)}"
                )
            ),
        ]
    )
    index_path = project_dir / "index.html"
    index_path.write_text(result.html, encoding="utf-8")
    return {"html": result.html}


async def renderer_node(state: ResearchState) -> dict:
    log.info("renderer_node: lint + render")
    project_dir = Path(state["project_dir"])
    slug = state["slug"]
    await run_lint(project_dir)
    video_path = await run_render(project_dir)
    copy_styles_snapshot(project_dir, slug)
    log.info("renderer_node: video at %s", video_path)
    return {"video_path": str(video_path)}
