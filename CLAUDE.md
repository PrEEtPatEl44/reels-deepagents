# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# First-time setup (after pip install -r requirements.txt)
crawl4ai-setup                      # installs Playwright's Chromium for scraping
npx hyperframes doctor              # one-time: confirms Node/FFmpeg/Chrome for renders

# Full pipeline: searcher → analyst → writer → scripter → narrator → designer → builder → renderer
python main.py "your topic here"
python main.py -q "your topic"      # suppresses node logs (report still streams)

# Video-only mode — skips research, runs only scripter → … → renderer.
# Use this when iterating on video design so you don't re-run DuckDuckGo/crawl4ai.
python main.py "topic" --report-file ./sample_report.md
python main.py "topic" --report "inline short report text"
```

No test suite, linter, or build step — it's a single-process Python CLI driving `npx hyperframes` subprocesses.

## Architecture

A LangGraph `StateGraph` wires eight async nodes into a strict linear pipeline:

```
START → searcher → analyst → writer → scripter → narrator → designer → builder → renderer → END
```

Shared state is `ResearchState` (`state.py`), a `TypedDict` that accumulates `topic → research_findings → analysis → report → script, title, slug → project_dir, audio_path, transcript → design_brief → html → video_path`. Each node returns a partial dict which LangGraph merges.

Key design choices that aren't obvious from one file:

- **Hybrid agent architecture.** Research nodes (`searcher`, `analyst`, `writer`) use plain `ChatAnthropic` / `create_react_agent`. Video-generation nodes (`scripter`, `designer`, `builder`) are **LangChain deep agents** (`deepagents.create_deep_agent`). Narrator + renderer are pure subprocess calls with no LLM.
- **`nodes.py` is the only place LLMs are created.** `_llm()` builds `ChatAnthropic` with `MODEL = "claude-sonnet-4-6"`; the deep agents use the same model via `video.DEEP_AGENT_MODEL`. Change those two constants to swap models globally.
- **`searcher_node` uses a cached ReAct agent** (`_searcher` module-level singleton) wired to two tools from `tools.py`. The agent, not Python, decides which URLs to scrape.
- **`tools.py` keeps a single `AsyncWebCrawler` alive** as `_crawler` behind an `asyncio.Lock` to avoid paying Playwright browser-spin-up cost per scrape. Scrape output is truncated to `MAX_SCRAPE_CHARS = 8000`.
- **No HyperFrames rules, colors, fonts, or HTML live in Python.** The three video-gen agents get a `FilesystemBackend(root_dir=REPO_ROOT, virtual_mode=True)` and can `ls`/`read_file`/`glob`/`grep` the full `skills/` tree on demand. There is no pre-selected skill-file bundle — the agent decides what to read based on its task. All visual decisions are made by the agents, not hardcoded.
- **Permissions are scoped per run.** `video.build_video_agent(project_relpath=...)` grants read+write only on the project's own subtree, read on `/skills/**` and `/.agents/skills/**` (the repo uses symlinks), and denies all other writes. The scripter runs read-only with no project subtree.
- **Scripter returns structured output** (`ScriptOut` via `response_format`). Designer and builder write their artifacts directly to disk via the deep agent's `write_file` tool; Python reads the real files back from `project_dir` after each node returns.
- **`narrator_node` scaffolds a fresh per-run project** at `outputs/videos/<slug>/` via `npx hyperframes init --non-interactive --skip-skills --skip-transcribe`, then runs `hyperframes tts` and `hyperframes transcribe` as subprocesses. If the slug directory already exists it's wiped first so re-runs start clean.
- **`renderer_node` copies the final `DESIGN.md` and `index.html` into `styles/<slug>/`** via `copy_styles_snapshot` so the generated style guides survive past the render as reference material.
- **Builder contract enforces two invariants via prompt**, not code: (1) word-synced captions rendered from the transcript, (2) an Instagram follow overlay in the final 2–3 s. The `builder_node` passes the full word-level transcript JSON into the user message, and computes `total_duration = spoken_end + 3` so the composition has room for the overlay.

## Two things to know before editing

- **To change visual/motion behavior**, edit `prompts.py::DESIGNER_SYSTEM` / `BUILDER_SYSTEM`. Agents discover their own reference files by browsing `/skills/` — no allowlist to maintain. Don't hardcode colors, fonts, or HTML anywhere.
- **`main.py` lazy-imports `nodes` inside `run_video_only`** so `--report-file` mode doesn't pull in crawl4ai/Playwright at parse time. Preserve that if you touch the CLI path.

## Gotchas

- `crawl4ai` needs Playwright's Chromium: `crawl4ai-setup` (one-time).
- `npx hyperframes` requires Node ≥ 22 and FFmpeg on `PATH`. Run `npx hyperframes doctor` if a render fails.
- TTS downloads the Kokoro model on first run; transcribe downloads the Whisper model on first run. Both are one-time per machine.
- `ANTHROPIC_API_KEY` is required; DuckDuckGo search needs no key.
- `outputs/videos/<slug>/` is nuked and rebuilt on every run with the same slug — nothing under it is durable. Persistent reference copies of `DESIGN.md` + `index.html` live in `styles/<slug>/`.
