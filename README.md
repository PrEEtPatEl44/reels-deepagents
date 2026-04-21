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

Three stages inside `photo_generator_node`, all using Claude:

1. **Plan** — one structured-output call returns 5–8 `Slide`s with `role`,
   `headline`, `body`. First role is always `hook`, last is always `cta`.
2. **Design** — one structured-output call *per slide*, run in parallel via
   `asyncio.gather`. The model returns a full 1080×1080 SVG document. The only
   things Python provides are (a) the design brief and (b) the specific slide's
   copy — the layout, composition, and visual choices are the model's.
3. **Assemble** — each SVG is validated with `xml.etree.ElementTree.fromstring`;
   a failed slide gets one retry and then a minimal fallback. Valid SVGs are
   rasterized by `cairosvg` to 1080×1080 PNG and zipped with `caption.txt`.

### The vibe brief (`prompts.py::SVG_DESIGNER_SYSTEM`)

The designer prompt locks down the feel without dictating layout:

| Aspect | Direction |
|--------|-----------|
| Mood | Editorial, confident, warm. New Yorker typography × indie tech newsletter. |
| Palette | Cream `#F0EEE6`, ink `#1F1F1F`, terracotta `#CC785C`, muted `#8C8C8C`. CTA slides invert to dark bg. |
| Typography | `Inter, "Helvetica Neue", Arial, "DejaVu Sans", sans-serif`. 800-weight headlines, tight tracking; 400–500 body; uppercase muted eyebrow labels. |
| Accents | Simple geometry only — a bar, a dot, a hairline. No illustrations, no emoji, no gradients. |
| Whitespace | 80px safe margin. One idea per slide. Let it breathe. |
| Rhythm | Same rails for every slide in a set — palette, font stack, margins — so slides feel like siblings, not strangers. |
| Role | `hook`: oversized headline + eyebrow label + "Swipe →". `body`: headline top, body mid. `cta`: inverted dark bg, restated takeaway, terracotta CTA line. |

Edit `SVG_DESIGNER_SYSTEM` in `prompts.py` to change the vibe (e.g. swap palette,
lean more playful, pick different typography). No code changes needed.

Fonts: DejaVu Sans is the reliable last-resort font in the stack since Cairo
needs an actually-installed font file on the system — it ships with most Linux
distros. Install Inter via `fc-cache` if you want the intended look.

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
- **Fonts look generic** → Inter isn't installed; DejaVu Sans is being used. To
  get Inter, install it (`fc-cache`) or bundle a TTF via `@font-face` inside the
  SVG templates in `carousel.py`.
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
