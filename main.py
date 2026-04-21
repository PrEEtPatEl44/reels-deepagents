import argparse
import asyncio
import logging
import sys

from dotenv import load_dotenv

from graph import build_graph


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )


async def run(topic: str, stream_writer: bool = True) -> dict:
    graph = build_graph()

    if not stream_writer:
        final = await graph.ainvoke({"topic": topic})
        return final

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Deep research + Instagram carousel pipeline.")
    parser.add_argument("topic", nargs="+", help="Research topic")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress node logs")
    args = parser.parse_args()

    load_dotenv()
    _setup_logging(verbose=not args.quiet)

    topic = " ".join(args.topic)
    final = asyncio.run(run(topic))

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
