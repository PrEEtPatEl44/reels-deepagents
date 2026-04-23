# Deep Research + HyperFrames Video Pipeline

A LangGraph pipeline that researches a topic on the web, writes a polished markdown
report, and turns that report into a high-quality short-form vertical video (9:16)
via **HyperFrames** (HTML/GSAP rendering).

Running on **Anthropic Claude 3.5 Sonnet** with **crawl4ai** for web scraping and
**DuckDuckGo** (via `ddgs`) for web search.

---

## What it does

Given a topic, the graph runs eight nodes in sequence:

```
START → searcher → analyst → writer → scripter → narrator → designer → builder → renderer → END
```

1.  **searcher** — A ReAct agent that searches DuckDuckGo and scrapes URLs via crawl4ai.
2.  **analyst** — Synthesizes findings, identifying themes and contradictions.
3.  **writer** — Produces a final markdown report with citations.
4.  **scripter** — Condenses the report into a 20–35 second narration script.
5.  **narrator** — Generates audio via TTS (Kokoro) and a word-level transcript (Whisper).
6.  **designer** — A "Deep Agent" that browses `/skills/` docs to define visual identity in `DESIGN.md`.
7.  **builder** — A "Deep Agent" that authors the `index.html` composition using HTML/GSAP.
8.  **renderer** — Lints and renders the composition to an `.mp4` via FFmpeg/Chrome.

Final state carries the report, script, and absolute path to the rendered video.

---

## Requirements

- Python 3.11+
- Node.js (for `npx hyperframes`)
- FFmpeg installed on your system
- API key:
  - `ANTHROPIC_API_KEY` — https://console.anthropic.com

---

## Install

```bash
pip install -r requirements.txt

# One-time: install the headless Chromium for crawl4ai.
crawl4ai-setup

# Verify HyperFrames environment
npx hyperframes doctor

cp .env.example .env
# edit .env and fill in ANTHROPIC_API_KEY
```

---

## Run

```bash
# Full research and video generation
python main.py "Nebius Token Factory features, capabilities, and applications"
```

Output:
- Node-by-node logs (unless `-q` is used).
- The writer's report streams to stdout.
- Final MP4 path is printed at the end.

### Video-only mode (skip the research pipeline)

When iterating on video design, supply a pre-written report to skip the research phase:

```bash
python main.py "topic" --report-file ./sample_report.md
```

---

## Live observability UI

A small FastAPI dashboard tails each run and shows every stage, tool call, and
subprocess line in real time — plus the artifact each stage produces as source
(report.md, script.txt, DESIGN.md, index.html, transcript.json, final mp4).

```bash
# Terminal A — start the observer (once)
python server.py
# open http://127.0.0.1:8000/

# Terminal B — run the pipeline as normal
python main.py "your topic"
```

The UI auto-switches to the newest run. Events land in `outputs/events/<run_id>.jsonl`;
the CLI writes them even if no server is listening, so historical runs can be replayed
by selecting them from the server's listing.

---

## Project layout

```
agents/
├── main.py          # CLI entry; handles full/video-only modes
├── graph.py         # build_graph(): StateGraph definition
├── state.py         # ResearchState TypedDict
├── nodes.py         # Implementation of all LangGraph nodes
├── prompts.py       # System prompts for every node
├── tools.py         # Web search and scraping tools
├── video.py         # HyperFrames CLI wrappers and Deep Agent setup
├── events.py        # Observability event bus (per-run JSONL)
├── server.py        # FastAPI observer + SSE stream for the UI
├── ui/              # Static dashboard (index.html, app.js, style.css)
├── skills/          # Documentation and patterns for the agents (symlinked)
└── outputs/         # Generated videos, events/<run>.jsonl, and artifacts
```

---

## How the designers work

The `designer` and `builder` nodes use **Deep Agents** from the `deepagents` package. These agents are granted scoped filesystem access to the `/skills/` directory, allowing them to:
- Browse core authoring rules, palettes, and motion principles.
- Read GSAP and HyperFrames API references.
- Make informed architectural and aesthetic decisions based on documentation rather than hardcoded prompts.

All visual decisions (colors, fonts, layout, transitions) are authored by the LLM into `DESIGN.md` and `index.html` within a per-run project directory.
