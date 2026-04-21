import asyncio
import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from carousel import (
    CaptionOut,
    Slide,
    SlidePlan,
    SlideSVG,
    build_zip,
    fallback_svg,
    pick_accents,
    svg_to_png,
    validate_svg,
)
from prompts import (
    ANALYST_SYSTEM,
    CAPTION_SYSTEM,
    SEARCHER_SYSTEM,
    SLIDE_PLANNER_SYSTEM,
    SVG_DESIGNER_SYSTEM,
    WRITER_SYSTEM,
)

SLIDE_DESIGN_ATTEMPTS = 3
from state import ResearchState
from tools import RESEARCH_TOOLS

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


async def _design_slide(
    slide: Slide,
    index: int,
    total: int,
    topic: str,
    accent: str,
) -> bytes:
    """Ask the designer LLM for one slide's SVG, validate it, and rasterize to
    PNG. If anything fails — invalid XML, unresolved refs, a cairosvg crash —
    regenerate the slide. After all attempts fail, return a rendered fallback."""
    designer = _llm(max_tokens=8192, temperature=0.8).with_structured_output(SlideSVG)
    user_brief_base = (
        f"ACCENT FOR THIS SLIDE: {accent}\n"
        "(Use this exact hex for the badge, headline highlight words, the "
        "3px accent separator, the glow-gradient stops, the dot indicator "
        "for the current slide, the bottom-bar logo mark, and any card "
        "borders or icon-square tints. Every other element of the brand "
        "theme stays fixed as defined in your system prompt.)\n\n"
        "=== THIS SLIDE ===\n"
        f"Carousel topic: {topic}\n"
        f"Slide position: {index} of {total}\n"
        f"Slide role: {slide.role}\n"
        f"Headline: {slide.headline}\n"
        f"Body: {slide.body or '(none — headline-only slide)'}\n\n"
        "Design this single slide as a 1080×1080 SVG. Execute the brand "
        "theme precisely; vary only composition."
    )
    repair_hint = (
        "\n\nIMPORTANT: a previous attempt produced an SVG that could not be rendered. "
        "Avoid marker references (marker-start, marker-end, marker-mid), avoid filter/"
        "clipPath refs unless you also define them, avoid url(#...) references to IDs "
        "that don't exist in this same document, and keep the structure simple."
    )

    for attempt in range(1, SLIDE_DESIGN_ATTEMPTS + 1):
        user_brief = user_brief_base + (repair_hint if attempt > 1 else "")
        try:
            result: SlideSVG = await designer.ainvoke(
                [
                    SystemMessage(content=SVG_DESIGNER_SYSTEM),
                    HumanMessage(content=user_brief),
                ]
            )
        except Exception:  # noqa: BLE001
            log.exception("slide %d design call failed (attempt %d)", index, attempt)
            continue

        cleaned = validate_svg(result.svg)
        if not cleaned:
            log.warning("slide %d SVG failed XML validation (attempt %d)", index, attempt)
            continue

        png = svg_to_png(cleaned)
        if png is not None:
            return png
        log.warning(
            "slide %d SVG parsed but failed to render (attempt %d) — regenerating",
            index,
            attempt,
        )

    log.warning("slide %d: using fallback SVG after %d failed attempts", index, SLIDE_DESIGN_ATTEMPTS)
    fallback_png = svg_to_png(fallback_svg(slide.headline, index, total))
    if fallback_png is None:
        # Fallback SVG is hand-authored and known-safe; this branch should be unreachable.
        raise RuntimeError(f"Failed to render fallback for slide {index}")
    return fallback_png


async def photo_generator_node(state: ResearchState) -> dict:
    log.info("photo_generator_node: planning slides and caption")
    report = state.get("report", "")
    topic = state.get("topic", "carousel")

    # 1. Plan slide content (role + headline + body for each slide).
    planner = _llm(max_tokens=8192, temperature=0.5).with_structured_output(SlidePlan)
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

    # 2. Pick accent colors — one per slide, with hook and CTA bookended to
    #    the same accent. Chosen in Python (deterministic hash of the topic)
    #    so every parallel slide designer gets a stable assignment and the
    #    set stays coherent — no extra LLM call needed.
    total = len(plan.slides)
    accents = pick_accents(total, topic)
    log.info("photo_generator_node: accents %s", accents)

    # 3. Design all slides in parallel + write the caption in parallel.
    log.info("photo_generator_node: designing %d slides in parallel", total)

    captioner = _llm(max_tokens=2048, temperature=0.7).with_structured_output(CaptionOut)
    caption_task = captioner.ainvoke(
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

    svg_tasks = [
        _design_slide(slide, i, total, topic, accents[i - 1])
        for i, slide in enumerate(plan.slides, start=1)
    ]

    pngs, cap = await asyncio.gather(asyncio.gather(*svg_tasks), caption_task)

    zip_path = build_zip(
        pngs=pngs,
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
