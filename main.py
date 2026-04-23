import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

import events
from graph import build_graph


def _setup_logging(verbose: bool) -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO if verbose else logging.WARNING)
    fmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    root.addHandler(stream)
    # Always attach the event-bus handler, regardless of verbose.
    # It honors its own level; INFO is reasonable.
    bridge = events.EventLogHandler()
    bridge.setLevel(logging.INFO)
    root.addHandler(bridge)


async def run_full(topic: str) -> dict:
    """Full pipeline: searcher → analyst → writer → scripter → narrator → designer → builder → renderer."""
    graph = build_graph()

    final_state: dict = {}
    print("\n=== REPORT ===\n", flush=True)
    async for event in graph.astream(
        {"topic": topic},
        stream_mode=["messages", "values"],
    ):
        mode, payload = event if isinstance(event, tuple) and len(event) == 2 else (None, event)
        if mode == "messages":
            chunk, metadata = payload
            if metadata.get("langgraph_node") == "writer":
                text = getattr(chunk, "content", "")
                if isinstance(text, list):
                    text = "".join(
                        b.get("text", "") for b in text if isinstance(b, dict) and b.get("type") == "text"
                    )
                if text:
                    print(text, end="", flush=True)
        elif mode == "values":
            final_state = payload
    print("\n", flush=True)
    return final_state


async def run_video_only(topic: str, report: str) -> dict:
    """Skip research — run only the video-generation tail against a given report."""
    from nodes import (
        builder_node,
        designer_node,
        narrator_node,
        renderer_node,
        scripter_node,
    )

    # Mark upstream research stages as skipped so the UI strip fills in.
    for skipped in ("searcher", "analyst", "writer"):
        events.emit("stage_start", stage=skipped)
        events.emit("stage_end", stage=skipped, status="skipped")

    state: dict = {"topic": topic, "report": report}
    for node in (scripter_node, narrator_node, designer_node, builder_node, renderer_node):
        produced = await node(state)
        state.update(produced)
    return state


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deep research + HyperFrames video pipeline.",
    )
    parser.add_argument("topic", nargs="+", help="Research topic (or video seed when using --report-file).")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress node logs.")
    src = parser.add_mutually_exclusive_group()
    src.add_argument(
        "--report-file",
        type=Path,
        metavar="PATH",
        help=(
            "Skip research; read the report from this file and run only the "
            "video-generation pipeline. Useful for iterating on video design."
        ),
    )
    src.add_argument(
        "--report",
        type=str,
        metavar="TEXT",
        help="Skip research; use this inline string as the report (for short snippets).",
    )
    args = parser.parse_args()

    load_dotenv()
    _setup_logging(verbose=not args.quiet)

    topic = " ".join(args.topic)

    mode = "video-only" if (args.report_file or args.report) else "full"
    run_id = events.start_run(topic=topic, mode=mode)
    print(
        f"[observability] run {run_id} — live UI: http://127.0.0.1:8000/  "
        f"(start server with: python server.py)",
        flush=True,
    )

    status = "ok"
    err: str | None = None
    try:
        if args.report_file or args.report:
            if args.report_file:
                if not args.report_file.exists():
                    print(f"error: report file not found: {args.report_file}", file=sys.stderr)
                    events.end_run(status="error", error="report file not found")
                    return 2
                report = args.report_file.read_text(encoding="utf-8")
            else:
                report = args.report
            print(f"[video-only mode] using report of {len(report)} chars; topic={topic!r}")
            final = asyncio.run(run_video_only(topic, report))
        else:
            final = asyncio.run(run_full(topic))
    except BaseException as e:  # Ctrl-C or otherwise
        status = "error"
        err = f"{type(e).__name__}: {e}"
        events.end_run(status=status, error=err)
        raise
    else:
        events.end_run(status=status)

    video_path = final.get("video_path")
    if video_path:
        print(f"Video: {video_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
