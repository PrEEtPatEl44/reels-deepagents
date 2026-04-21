import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from carousel import CaptionOut, SlidePlan, render_carousel
from mcp_client import get_scrapegraph_tools
from prompts import (
    ANALYST_SYSTEM,
    CAPTION_SYSTEM,
    SEARCHER_SYSTEM,
    SLIDE_PLANNER_SYSTEM,
    WRITER_SYSTEM,
)
from state import ResearchState

log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

# Singletons so we don't re-instantiate models or respawn the MCP child process per run.
_searcher = None
_mcp_client = None


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


async def _get_searcher():
    global _searcher, _mcp_client
    if _searcher is None:
        tools, client = await get_scrapegraph_tools()
        _mcp_client = client  # keep the stdio child alive
        _searcher = create_react_agent(_llm(max_tokens=8192), tools, prompt=SEARCHER_SYSTEM)
        log.info("Loaded %d ScrapeGraph MCP tools: %s", len(tools), [t.name for t in tools])
    return _searcher


async def searcher_node(state: ResearchState) -> dict:
    log.info("searcher_node: researching topic %r", state["topic"])
    agent = await _get_searcher()
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


async def photo_generator_node(state: ResearchState) -> dict:
    log.info("photo_generator_node: planning slides and caption")
    report = state.get("report", "")
    topic = state.get("topic", "carousel")

    planner = _llm(max_tokens=4096, temperature=0.5).with_structured_output(SlidePlan)
    plan = await planner.ainvoke(
        [
            SystemMessage(content=SLIDE_PLANNER_SYSTEM),
            HumanMessage(
                content=(
                    f"Topic: {topic}\n\n"
                    f"Report to condense into carousel slides:\n\n{report}"
                )
            ),
        ]
    )

    captioner = _llm(max_tokens=2048, temperature=0.7).with_structured_output(CaptionOut)
    cap = await captioner.ainvoke(
        [
            SystemMessage(content=CAPTION_SYSTEM),
            HumanMessage(
                content=(
                    f"Topic: {topic}\n\n"
                    f"Carousel slide plan (for alignment):\n{plan.model_dump_json(indent=2)}\n\n"
                    f"Full report (for factual grounding):\n\n{report}"
                )
            ),
        ]
    )

    zip_path = render_carousel(
        plan=plan,
        caption=cap.caption,
        hashtags=cap.hashtags,
        topic=topic,
    )
    log.info("photo_generator_node: wrote carousel ZIP to %s", zip_path)
    return {
        "slide_plan": [s.model_dump() for s in plan.slides],
        "caption": cap.caption,
        "carousel_zip_path": str(zip_path),
    }
