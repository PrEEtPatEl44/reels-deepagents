import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from graph import build_graph


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )


async def run_full(topic: str) -> dict:
    """Full pipeline: searcher → analyst → writer → photo_generator."""
    graph = build_graph()

    # Stream messages from the writer node only so the user sees the report live.
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


async def run_carousel_only(topic: str, report: str) -> dict:
    """Skip research — run only the photo_generator node against a given report."""
    # Import lazily so this path doesn't pull in the searcher/crawl4ai deps at parse time.
    from nodes import photo_generator_node

    state = {"topic": topic, "report": report}
    produced = await photo_generator_node(state)
    return {**state, **produced}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deep research + Instagram carousel pipeline.",
    )
    parser.add_argument("topic", nargs="+", help="Research topic (or caption seed when using --report-file).")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress node logs.")
    src = parser.add_mutually_exclusive_group()
    src.add_argument(
        "--report-file",
        type=Path,
        metavar="PATH",
        help=(
            "Skip research; read the report from this file and run only the "
            "photo_generator node. Useful for iterating on slide design."
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

    if args.report_file or args.report:
        if args.report_file:
            if not args.report_file.exists():
                print(f"error: report file not found: {args.report_file}", file=sys.stderr)
                return 2
            report = args.report_file.read_text(encoding="utf-8")
        else:
            report = args.report
        print(f"[carousel-only mode] using report of {len(report)} chars; topic={topic!r}")
        final = asyncio.run(run_carousel_only(topic, report))
    else:
        final = asyncio.run(run_full(topic))

    zip_path = final.get("carousel_zip_path")
    caption = final.get("caption")
    if zip_path:
        print(f"Carousel ZIP: {zip_path}")
    if caption:
        print("\n=== CAPTION ===\n")
        print(caption)
    return 0


if __name__ == "__main__":
    sys.exit(main())
