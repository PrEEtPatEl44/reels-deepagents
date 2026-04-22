# GEMINI.md

## Project Overview
This project is a **Deep Research + HyperFrames Video Pipeline**. It automates the end-to-end process of researching a topic on the web, synthesizing findings into a report, and transforming that report into a high-quality, short-form 9:16 video (suitable for Instagram Reels or TikTok).

The pipeline leverages **LangGraph** for orchestration, **Claude 3.5 Sonnet** as the reasoning engine, and **HyperFrames** as the HTML/SVG/GSAP-based video rendering engine.

### Key Technologies
- **LangGraph**: Orchestrates the multi-node research and video generation state machine.
- **Anthropic Claude 3.5 Sonnet**: Used for research, writing, and as a "Deep Agent" for design and composition.
- **crawl4ai**: Headless browser-based web scraping.
- **DuckDuckGo (ddgs)**: Web search tool.
- **HyperFrames CLI**: Handles project scaffolding, TTS (Kokoro), transcription (Whisper), linting, and rendering (FFmpeg/Chrome).
- **deepagents**: A specialized framework granting LLMs scoped filesystem access to browse skill documentation and author project files.

---

## Architecture
The pipeline consists of eight sequential nodes in a `StateGraph`:

### Research Phase
1.  **searcher**: A ReAct agent using `web_search` and `scrape_url` tools to gather raw data.
2.  **analyst**: Synthesizes findings, identifies themes, and preserves verified references.
3.  **writer**: Produces a polished markdown report with an engaging intro and structured sections.

### Video Phase
4.  **scripter**: Condenses the report into a 20–35 second narration script (structured output).
5.  **narrator**: Scaffolds the project, generates audio via TTS, and produces a word-level transcript.
6.  **designer**: A Deep Agent that browses `/skills/` to author a `DESIGN.md` defining the visual identity.
7.  **builder**: A Deep Agent that authors the `index.html` composition based on `DESIGN.md` and the transcript.
8.  **renderer**: Lints the composition and renders it to a final `.mp4` file.

---

## Building and Running

### Prerequisites
- Python 3.11+
- Node.js (for `npx hyperframes`)
- FFmpeg installed on `PATH`
- Anthropic API Key in `.env`

### Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup Playwright for crawl4ai
crawl4ai-setup

# Verify HyperFrames environment
npx hyperframes doctor
```

### Execution
```bash
# Full Pipeline (Research + Video)
python main.py "Your topic here"

# Video-Only Mode (Useful for iterating on design)
python main.py "Your topic" --report-file ./path/to/report.md

# Quiet Mode (Suppress node logs)
python main.py -q "Your topic"
```

---

## Development Conventions

### Hybrid Agent Strategy
- **Research nodes** use standard `ChatAnthropic` or `create_react_agent`.
- **Video nodes** (`scripter`, `designer`, `builder`) use `deepagents` with filesystem permissions.
- **Logic placement**: Avoid hardcoding visual styles (colors, fonts, HTML structure) in Python. Instead, update the system prompts in `prompts.py` or the reference files in `skills/` to influence the agentic designers.

### Filesystem & Skills
- The `skills/` directory (linked to `.agents/skills/`) is the authoritative source of truth for the agents. It contains documentation for HyperFrames, GSAP, and design patterns.
- **Project Isolation**: Every run generates a fresh project in `outputs/videos/<slug>/`. This directory is wiped on every run with the same slug.
- **Style Snapshots**: After rendering, `DESIGN.md` and `index.html` are copied to `styles/<slug>/` for long-term reference.

### Model Configuration
- Primary model: `claude-sonnet-4-6`.
- Model constants are located in `nodes.py::MODEL` and `video.py::DEEP_AGENT_MODEL`.

### Subprocess Orchestration
- `video.py` contains async wrappers for `npx hyperframes` commands.
- Use `video.run_tts`, `video.run_transcribe`, and `video.run_render` for CLI interactions.
