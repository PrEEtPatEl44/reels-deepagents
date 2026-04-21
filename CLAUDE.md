# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# First-time setup (after pip install -r requirements.txt)
crawl4ai-setup                      # installs Playwright's Chromium for scraping

# Full pipeline: search → analyst → writer → photo_generator
python main.py "your topic here"
python main.py -q "your topic"      # suppresses node logs (report still streams)

# Carousel-only mode — skips research, runs only photo_generator.
# Use this when iterating on slide design so you don't re-run DuckDuckGo/crawl4ai.
python main.py "topic" --report-file ./sample_report.md
python main.py "topic" --report "inline short report text"
```

No test suite, linter, or build step — it's a single-process Python CLI.

## Architecture

A LangGraph `StateGraph` wires four async nodes into a strict linear pipeline:

```
START → searcher → analyst → writer → photo_generator → END
```

Shared state is `ResearchState` (`state.py`), a `TypedDict` that accumulates `topic → research_findings → analysis → report → slide_plan, caption, carousel_zip_path`. Each node returns a partial dict which LangGraph merges.

Key design choices that aren't obvious from one file:

- **`nodes.py` is the only place LLMs are created.** `_llm()` builds `ChatAnthropic` with `MODEL = "claude-sonnet-4-6"` — change this one constant to swap models globally. Per-call `max_tokens`/`temperature` are passed at the call site.
- **`searcher_node` uses a cached ReAct agent** (`_searcher` module-level singleton from `langgraph.prebuilt.create_react_agent`) wired to two tools from `tools.py`. The agent, not Python, decides which URLs to scrape.
- **`tools.py` keeps a single `AsyncWebCrawler` alive** as `_crawler` behind an `asyncio.Lock` to avoid paying Playwright browser-spin-up cost per scrape. Scrape output is truncated to `MAX_SCRAPE_CHARS = 8000`.
- **`photo_generator_node` does three things in one node:** (1) structured-output `SlidePlan` (5–8 `Slide`s with roles hook/body/cta, enforced by the pydantic model in `carousel.py`), (2) `pick_accents(total, topic)` assigns accents *in Python* from a deterministic SHA-256 hash of the topic — no extra LLM call — with the hook and CTA bookended to the same color, (3) `asyncio.gather` runs one per-slide `_design_slide` coroutine for SVG generation in parallel alongside the caption call.
- **SVG designer has a retry-with-repair loop.** `_design_slide` loops up to `SLIDE_DESIGN_ATTEMPTS = 3`: validate via `validate_svg` (XML parse + `<svg>` root check in `carousel.py`), then trial-render via `svg_to_png` (cairosvg). On failure it re-prompts with `repair_hint` (warns against unresolved `url(#...)` / marker refs). If all attempts fail, it falls back to the hand-authored `fallback_svg` so runs never crash.
- **Brand consistency is structural, not semantic.** Every parallel designer call gets the identical `SVG_DESIGNER_SYSTEM` prompt (full brand theme — background stack, typography, components, bottom bar). Only the accent hex in the user message varies per slide. Background/typography/margins are effectively fixed across the set.

## Two things to know before editing

- **To tweak visual design**, edit `prompts.py::SVG_DESIGNER_SYSTEM` (theme) and/or `carousel.py::ACCENT_PALETTE` (color rotation). Don't hardcode colors into the designer prompt — the per-slide accent is injected by `_design_slide` at call time.
- **`main.py` lazy-imports `nodes` inside `run_carousel_only`** so `--report-file` mode doesn't pull in crawl4ai/Playwright at parse time. Preserve that if you touch the CLI path.

## Gotchas

- `cairosvg` needs native libs: `sudo apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0`.
- `crawl4ai` needs Playwright's Chromium: `crawl4ai-setup` (one-time).
- `ANTHROPIC_API_KEY` is required; DuckDuckGo search needs no key.
- Fonts: the theme references SF Pro Display / SF Mono. Without them installed in the OS, cairo falls back to DejaVu Sans and the carousel looks generic.
