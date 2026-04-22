# AGENTS.md

## Essential Commands

```bash
# First-time setup
pip install -r requirements.txt
crawl4ai-setup  # Install Playwright's Chromium for scraping

# Full pipeline: search → analyst → writer → photo_generator
python main.py "your topic here"
python main.py -q "your topic"  # Quiet mode (suppresses node logs)

# Carousel-only mode (skip research, useful for iterating on slide design)
python main.py "topic" --report-file ./sample_report.md
python main.py "topic" --report "inline short report text"
```

## Architecture

LangGraph pipeline with 4 sequential nodes:
```
START → searcher → analyst → writer → photo_generator → END
```

Shared state (`ResearchState`): accumulates `topic → research_findings → analysis → report → slide_plan, caption, carousel_zip_path`

Key implementation details:
- `nodes.py` is the only file that creates LLMs (`MODEL = "claude-sonnet-4-6"`)
- `searcher_node` uses a cached ReAct agent with two tools: `web_search` and `scrape_url`
- `photo_generator_node` does three things in one node:
  1. Structured-output `SlidePlan` (5–8 slides with roles hook/body/cta)
  2. `pick_accents(total, topic)` assigns colors deterministically from SHA-256 hash
  3. Parallel `_design_slide` coroutines for SVG generation with retry-with-repair loop

## Critical Requirements

- `ANTHROPIC_API_KEY` in `.env` (required)
- Native libs for `cairosvg`: `sudo apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0`
- Playwright's Chromium: `crawl4ai-setup` (one-time setup)
- Fonts: SF Pro Display / SF Mono preferred, falls back to DejaVu Sans

## Key Files

- `main.py` - CLI entry point with full and carousel-only modes
- `graph.py` - LangGraph wiring (`StateGraph` compilation)
- `nodes.py` - Implementation of all four pipeline nodes
- `prompts.py` - System prompts for every node
- `tools.py` - `web_search` and `scrape_url` LangChain tools
- `carousel.py` - Slide planning, SVG validation, PNG rendering, ZIP packaging
- `state.py` - `ResearchState` TypedDict definition

## Gotchas

- Lazy imports in `main.py` for `--report-file` mode (doesn't pull in crawl4ai/Playwright)
- SVG designer has 3 attempts with repair hints; falls back to minimal SVG on failure
- Slide accents are deterministic SHA-256 hash of topic (hook and CTA share same accent)
- All designer calls get identical system prompt; only accent hex varies per slide
- To change visual design: edit `prompts.py::SVG_DESIGNER_SYSTEM` or `carousel.py::ACCENT_PALETTE`
- `tools.py` keeps a single `AsyncWebCrawler` alive behind `asyncio.Lock` to avoid browser spin-up cost