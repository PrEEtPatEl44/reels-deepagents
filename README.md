# Deep Research + Instagram Carousel Pipeline

A LangGraph pipeline that researches a topic on the web, writes a polished markdown
report, and turns that report into an Instagram carousel (ZIP of 1080×1080 PNGs +
ready-to-post caption).

Running on **Anthropic Claude Sonnet 4.6** with **crawl4ai** for web scraping and
**DuckDuckGo** (via `ddgs`) for web search. No MCP servers, no paid scraping APIs.

---

## What it does

Given a topic, the graph runs four nodes in sequence:

```
START → searcher → analyst → writer → photo_generator → END
```

1. **searcher** — a LangGraph ReAct agent with two tools:
   - `web_search(query, max_results)` — DuckDuckGo search, no API key.
   - `scrape_url(url)` — crawl4ai headless-browser scrape, returns markdown.

   The agent searches, picks promising URLs, scrapes them, and compiles raw
   findings with real citations.
2. **analyst** — a plain `ChatAnthropic` call that synthesizes the findings,
   identifies themes and contradictions, and passes forward only the URLs that
   were actually present in the researcher's output (no hallucinated links).
3. **writer** — produces a final markdown report: intro → sections → recommendations
   → References. Streams tokens live to the terminal.
4. **photo_generator** — takes the report and produces:
   - A **slide plan** (5–8 slides with `role ∈ {hook, body, cta}`) via structured
     output — this decides *what* each slide says.
   - A **caption + hashtags** via structured output.
   - For each slide, an **SVG designer pass** where Claude writes the full SVG
     markup itself, guided only by a design brief (vibe, palette, typography,
     role-specific tone). Designs run in parallel.
   - Each SVG is validated (XML parse + `<svg>` root check) with one retry; on
     hard failure a minimal fallback SVG is used so the run never crashes.
   - SVGs → PNGs (`cairosvg`) → ZIP to `./outputs/<slug>-<timestamp>.zip`.

Final state carries the report, caption, and absolute ZIP path.

---

## Requirements

- Python 3.11+
- Native libs for `cairosvg` (Debian/Ubuntu/WSL):
  ```bash
  sudo apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
  ```
- Playwright browsers for `crawl4ai` (installed via post-install step below).
- API key:
  - `ANTHROPIC_API_KEY` — https://console.anthropic.com

(No key is required for DuckDuckGo search.)

---

## Install

```bash
pip install -r requirements.txt

# One-time: install the headless Chromium that crawl4ai drives.
crawl4ai-setup
# If that command isn't on PATH, equivalent:
#   python -m playwright install chromium --with-deps

cp .env.example .env
# edit .env and fill in ANTHROPIC_API_KEY
```

---

## Run

```bash
python main.py "Nebius Token Factory features, capabilities, and applications"
```

Output:
- Node-by-node log lines to stderr (searcher → analyst → writer → photo_generator).
- The writer's report streams to stdout in real time.
- A final block prints:
  ```
  Carousel ZIP: /abs/path/to/outputs/<slug>-<timestamp>.zip

  === CAPTION ===
  <caption text with hashtags>
  ```

Quiet mode (suppress node logs, still streams the report):
```bash
python main.py -q "your topic here"
```

### Carousel-only mode (skip the research pipeline)

When you're iterating on the photo_generator — slide design, vibe prompt,
palette — you don't want to pay for a full research run every time. Supply a
pre-written report and only the photo_generator node runs:

```bash
# from a file
python main.py "nebius token factory" --report-file ./sample_report.md

# inline (short snippets only)
python main.py "langgraph agents" --report "LangGraph is a framework for..."
```

The `topic` positional arg is still used (for the caption, slide planner
context, and ZIP filename). The search/analyst/writer nodes are skipped
entirely — nothing hits DuckDuckGo or crawl4ai in this mode.

Unzip to inspect:
```bash
unzip -l outputs/<file>.zip          # lists slide_01.png ... slide_0N.png + caption.txt
unzip -p outputs/<file>.zip caption.txt
```

---

## Project layout

```
agents/
├── main.py          # CLI entry; streams writer tokens; prints final ZIP + caption
├── graph.py         # build_graph(): StateGraph wiring + compile
├── state.py         # ResearchState TypedDict
├── nodes.py         # searcher/analyst/writer/photo_generator node implementations
├── prompts.py       # system prompts for every node
├── tools.py         # web_search (ddgs) and scrape_url (crawl4ai) LangChain tools
├── carousel.py      # SlidePlan model, SVG templates, cairosvg render, ZIP packaging
├── requirements.txt
├── .env.example
└── outputs/         # generated carousel ZIPs land here (gitignored)
```

---

## How the research tools work

`tools.py` exposes two LangChain `@tool` functions directly to the ReAct agent —
no MCP wrapper, no subprocess orchestration:

- **`web_search(query, max_results)`** — uses `ddgs` (DuckDuckGo) in a worker
  thread. Returns a list of `{title, url, snippet}` dicts. Free, no API key.
- **`scrape_url(url)`** — uses `crawl4ai.AsyncWebCrawler` (a headless browser
  powered by Playwright) to fetch a page and return clean markdown. The crawler
  is instantiated once as a module-level singleton and reused across calls to
  avoid paying the browser-spin-up cost on every scrape. Output is capped at
  ~8000 chars per page to keep the agent's context manageable.

The searcher's system prompt tells it to: run 1–3 searches → pick 3–6 URLs →
scrape each → compile findings with a References section containing ONLY URLs
that were successfully scraped.

Why not MCP? For a single-process pipeline like this, direct Python tools are
simpler, faster (no stdio round-trip), and have fewer moving parts. MCP shines
when you want to share a server across multiple clients — not the case here.

---

## How the carousel is built

Three stages inside `photo_generator_node`:

1. **Plan** — one structured-output call returns 5–8 `Slide`s with `role`,
   `headline`, `body`. First role is always `hook`, last is always `cta`.
2. **Design** — one fixed brand theme, one rotating accent per slide. Python
   calls `carousel.pick_accents(total, topic)` which assigns a hex accent to
   every slide (deterministic SHA-256 hash of the topic). Hook and CTA slides
   are bookended to the same accent; body slides rotate through the remaining
   palette. Then a structured-output designer call runs *per slide* in
   parallel via `asyncio.gather`. Every call gets the same system prompt (the
   full brand-theme spec: background, typography, components, bottom bar,
   margins) plus its own assigned accent hex.
3. **Assemble** — each SVG is validated (`xml.etree.ElementTree.fromstring`
   plus a trial render via cairosvg); a failed slide gets up to 3 attempts
   with a repair hint, then a minimal fallback. Valid SVGs are rasterized by
   `cairosvg` to 1080×1080 PNG and zipped with `caption.txt`.

### The brand theme

`prompts.py::SVG_DESIGNER_SYSTEM` pins a single brand theme that every slide
executes:

- **Background**: near-black `#0A0A0F` with a linear gradient tinted by the
  slide's accent at the midpoint, plus radial accent glows at upper-right
  and lower-left, ~3% fractal-noise grain, and faint vertical guide lines
  at x=72 / x=1008.
- **Typography**: SF Pro Display for display/body, SF Mono for code/labels
  (both with system fallbacks). Headlines 62–110px weight 800 letter-spacing
  -2 to -4; body 22–28px; badge labels 19px uppercase letter-spacing +3.
- **Layout**: 72px left/right safe margins, bottom bar anchored at y=1000
  with a brand-initial circle mark on the left and a dot row on the right
  (current slide is an elongated accent pill).
- **Components**: filled accent badges on the hook, outlined elsewhere;
  terminal blocks with traffic-light dots and mono prompts; step cards,
  comparison tables with faint white dividers.
- **Engagement cues**: circular "Swipe →" affordance on the hook, gradient
  "FOLLOW FOR MORE →" pill with faint Save/Share/Comment capsules on the CTA.

### Rotating accents

The one element that changes slide-to-slide is the accent color. Python
picks accents deterministically from a fixed palette (red → orange →
gold → green → purple → cyan → pink) via
`carousel.pick_accents(total, topic)`. Hook and CTA slides share the same
accent (bookend effect); body slides walk through the remaining palette.
The accent drives the badge, headline highlight words, accent separator,
glow tint, current-slide dot, bottom-bar mark, and card borders.

### Consistency-by-construction

Because every parallel designer call receives the same system prompt (with
the full theme spec) and only the accent hex differs per slide, the whole
set shares identical background, typography, margins, and components. Only
composition (headline anchor, alignment, which supporting component appears)
varies. A viewer scrolling the carousel reads it as one deliberately
designed set with a color progression.

### Changing the vibe

- Edit `SVG_DESIGNER_SYSTEM` in `prompts.py` to tweak the background stack,
  typography, components, or engagement cues.
- Edit `ACCENT_PALETTE` in `carousel.py` to change the rotating color set
  or its order.
- To force a specific accent during testing, hardcode
  `accents = ["#FF3B30"] * total` in `photo_generator_node` instead of
  calling `pick_accents(total, topic)`.

Fonts: the brand theme references `SF Pro Display` / `SF Mono` with fallbacks
to `Helvetica Neue`, `Arial`, `DejaVu Sans`. Cairo needs an installed font
file to render, so install SF Pro (or a close substitute like Inter) via
`fc-cache` for the intended look — otherwise it falls back to DejaVu.

---

## Configuration knobs

- **Model** — `nodes.py::MODEL = "claude-sonnet-4-6"`. Swap to `claude-opus-4-7`
  for higher quality at higher cost, or `claude-haiku-4-5` for speed.
- **Slide count** — enforced in `carousel.py::SlidePlan` (5–8). Adjust the
  pydantic `min_length`/`max_length` to widen the range.
- **Design vibe** — `prompts.py::SVG_DESIGNER_SYSTEM`. Palette, typography,
  mood, and role-specific tone all live there.
- **Output directory** — `build_zip(outputs_dir=...)`. Default `./outputs/`.
- **Scrape length cap** — `tools.py::MAX_SCRAPE_CHARS`. Raise for denser sources,
  lower for tighter agent contexts.

---

## Verification

A minimal end-to-end smoke test:

```bash
# 1. Confirm the tools work standalone
python -c "
import asyncio
from dotenv import load_dotenv; load_dotenv()
from tools import web_search, scrape_url
async def main():
    hits = await web_search.ainvoke({'query': 'langgraph react agent', 'max_results': 3})
    print('search:', [h['url'] for h in hits])
    page = await scrape_url.ainvoke({'url': hits[0]['url']})
    print('scrape title:', page.get('title'), 'chars:', len(page.get('markdown', '')))
asyncio.run(main())
"

# 2. Full run
python main.py "impact of LangGraph on agent tooling"

# 3. Inspect the carousel
ls outputs/
unzip -l outputs/*.zip | tail
```

Expected after a full run:
- A ZIP containing `slide_01.png` … `slide_0N.png` + `caption.txt`.
- Each PNG is 1080×1080 with consistent palette/typography.
- Slide 1 is the hook; last slide is the CTA.
- Caption length < 2000 chars so it fits under Instagram's 2200-char limit with
  hashtags appended.

---

## Known gotchas

- **cairosvg import fails** → install the system libs listed under *Requirements*.
- **crawl4ai fails with "Executable doesn't exist"** → you skipped `crawl4ai-setup`.
  Run it now: `crawl4ai-setup` or `python -m playwright install chromium --with-deps`.
- **Fonts look generic** → SF Pro / Inter aren't installed; DejaVu Sans is
  being used. Install the desired family (`fc-cache`) for the intended look.
- **DuckDuckGo rate-limits / empty results** → try fewer, more specific queries
  or add a short backoff. `ddgs` is a free service with no guarantees.
- **`with_structured_output` validation error** → usually token pressure on long
  reports. Shorten the report or raise `max_tokens` on the planner/caption LLMs
  in `nodes.py::photo_generator_node`.
- **A slide shows the "VISUAL UNAVAILABLE" fallback** → the designer's SVG
  output didn't parse as XML after one retry. Check the log line
  `slide N SVG failed validation` and inspect the raw output. Raising the
  designer's `max_tokens` in `nodes.py::_design_slide` often fixes truncation.
- **Model access error** → `claude-sonnet-4-6` requires an Anthropic account with
  access to Claude 4 models. Error surfaces on first invocation.
