# Deep Research + Instagram Carousel Pipeline

A LangGraph pipeline that researches a topic on the web, writes a polished markdown
report, and turns that report into an Instagram carousel (ZIP of 1080×1080 PNGs +
ready-to-post caption).

Port of an earlier agno-based `DeepResearcherAgent`, now running on **Anthropic
Claude Sonnet 4.6** with **ScrapeGraph AI** wired in as an **MCP tool**.

---

## What it does

Given a topic, the graph runs four nodes in sequence:

```
START → searcher → analyst → writer → photo_generator → END
```

1. **searcher** — a LangGraph ReAct agent with access to ScrapeGraph MCP tools.
   Searches, scrapes, and extracts relevant sources on the topic. Returns raw
   research findings with real URLs.
2. **analyst** — a plain `ChatAnthropic` call that synthesizes the findings,
   identifies themes and contradictions, and passes forward only the URLs that
   were actually present in the researcher's output (no hallucinated links).
3. **writer** — produces a final markdown report: intro → sections → recommendations
   → References. Streams tokens live to the terminal.
4. **photo_generator** — takes the report and produces:
   - A **slide plan** (5–8 slides with `role ∈ {hook, body, cta}`) via structured output.
   - A **caption + hashtags** via structured output.
   - Each slide is rendered from a Python SVG template (consistent branding, no
     LLM-authored SVG fragility) and converted to PNG via `cairosvg`.
   - All PNGs + `caption.txt` are zipped into `./outputs/<slug>-<timestamp>.zip`.

Final state carries the report, caption, and absolute ZIP path.

---

## Requirements

- Python 3.11+
- `uvx` on PATH (from [astral-sh/uv](https://docs.astral.sh/uv/)) — used to launch the ScrapeGraph MCP server.
- Native libs for `cairosvg` (Debian/Ubuntu/WSL):
  ```bash
  sudo apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
  ```
- API keys:
  - `ANTHROPIC_API_KEY` — https://console.anthropic.com
  - `SGAI_API_KEY` — https://scrapegraphai.com

---

## Install

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and fill in ANTHROPIC_API_KEY + SGAI_API_KEY
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
├── mcp_client.py    # get_scrapegraph_tools() via langchain-mcp-adapters
├── carousel.py      # SlidePlan model, SVG templates, cairosvg render, ZIP packaging
├── requirements.txt
├── .env.example
└── outputs/         # generated carousel ZIPs land here (gitignored)
```

---

## How the MCP wiring works

`mcp_client.py` uses `MultiServerMCPClient` from `langchain-mcp-adapters` to spawn
`uvx scrapegraph-mcp` as a stdio child process and expose its tools as LangChain
`Tool` objects. Those tools are then handed to `create_react_agent(...)` in the
searcher node.

The client + child process are cached as module-level singletons in `nodes.py`
so they survive across graph steps and aren't respawned on every invocation.

If the `uvx scrapegraph-mcp` entry-point name changes upstream, swap to:
```python
"command": "uvx",
"args": ["--from", "scrapegraph-mcp", "<script-name>"],
```

---

## How the carousel is built

`carousel.py` defines three layout templates — `hook`, `body`, `cta` — with a
shared Anthropic-inspired palette:

| Role | Background | Ink | Accent |
|------|-----------|-----|--------|
| hook | `#F0EEE6` (cream) | `#1F1F1F` | `#CC785C` (terracotta) |
| body | `#F0EEE6` | `#1F1F1F` | `#CC785C` |
| cta  | `#1F1F1F` (inverted) | `#F0EEE6` | `#CC785C` |

Typography: `Inter, "Helvetica Neue", Arial, DejaVu Sans, sans-serif` (DejaVu is
the reliable fallback on headless Linux; Cairo needs an actual installed font
file to render).

Why templated SVG instead of letting the LLM author SVG directly? Two reasons:
1. **Reliability** — no malformed XML, no typography drift across slides, no
   palette drift. The renderer guarantees valid output every time.
2. **Consistency** — all slides in a run look like siblings, not strangers.

The LLM does what it's good at: condensing a report into punchy hook/body/cta
copy. Python does the pixels.

---

## Configuration knobs

- **Model** — `nodes.py::MODEL = "claude-sonnet-4-6"`. Swap to `claude-opus-4-7`
  for higher quality at higher cost, or `claude-haiku-4-5` for speed.
- **Slide count** — enforced in `carousel.py::SlidePlan` (5–8). Adjust the
  pydantic `min_length`/`max_length` to widen the range.
- **Palette / typography** — constants at the top of `carousel.py`.
- **Output directory** — `render_carousel(outputs_dir=...)`. Default `./outputs/`.

---

## Verification

A minimal end-to-end smoke test:

```bash
# 1. Confirm MCP tools load
python -c "
import asyncio
from dotenv import load_dotenv; load_dotenv()
from mcp_client import get_scrapegraph_tools
tools, _ = asyncio.run(get_scrapegraph_tools())
print([t.name for t in tools])
"

# 2. Full run
python main.py "impact of MCP on agent tooling"

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
- **Fonts look generic** → Inter isn't installed; DejaVu Sans is being used. To
  get Inter, install it (`fc-cache`) or bundle a TTF via `@font-face` inside the
  SVG templates in `carousel.py`.
- **MCP child process exits mid-run** → check that `_mcp_client` in `nodes.py` is
  actually held as a module-level ref; don't move it into a local scope.
- **`with_structured_output` validation error** → usually token pressure on long
  reports. Shorten the report or raise `max_tokens` on the planner/caption LLMs
  in `nodes.py::photo_generator_node`.
- **Model access error** → `claude-sonnet-4-6` requires an Anthropic account with
  access to Claude 4 models. Error surfaces on first invocation.
