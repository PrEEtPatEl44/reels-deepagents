"""
Research tools for the searcher agent.

Two tools are exposed:
  - web_search(query, max_results): DuckDuckGo search via `ddgs` (no API key).
  - scrape_url(url): crawl4ai headless-browser scrape, returns markdown.

These are plain LangChain tools — no MCP wrapper. The searcher ReAct agent
calls them directly.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from langchain_core.tools import tool

import events

log = logging.getLogger(__name__)

# Cap single-page scrape output to keep the agent's context manageable.
MAX_SCRAPE_CHARS = 8000

# crawl4ai loads Playwright on first use. Reuse a single AsyncWebCrawler across calls.
_crawler = None
_crawler_lock = asyncio.Lock()


async def _get_crawler():
    global _crawler
    async with _crawler_lock:
        if _crawler is None:
            from crawl4ai import AsyncWebCrawler  # lazy import: heavy deps

            _crawler = AsyncWebCrawler(verbose=False)
            await _crawler.start()
    return _crawler


async def close_crawler() -> None:
    """Call at shutdown to release the Playwright browser."""
    global _crawler
    if _crawler is not None:
        try:
            await _crawler.close()
        except Exception:  # noqa: BLE001
            log.exception("Failed to close crawl4ai crawler cleanly")
        _crawler = None


@tool
async def web_search(query: str, max_results: int = 6) -> list[dict[str, Any]]:
    """
    Search the web via DuckDuckGo and return the top results.

    Args:
        query: Free-text search query.
        max_results: Number of results to return (1-10). Defaults to 6.

    Returns:
        A list of {"title", "url", "snippet"} dicts.
    """
    from ddgs import DDGS  # lazy import

    n = max(1, min(int(max_results or 6), 10))

    def _search() -> list[dict[str, Any]]:
        with DDGS() as ddgs:
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href") or r.get("url", ""),
                    "snippet": r.get("body", ""),
                }
                for r in ddgs.text(query, max_results=n)
            ]

    events.emit("tool_call", stage="searcher", tool="web_search", args={"query": query, "n": n})
    # ddgs is sync; run in a worker thread so we don't block the event loop.
    results = await asyncio.to_thread(_search)
    log.info("web_search %r -> %d results", query, len(results))
    events.emit(
        "tool_result",
        stage="searcher",
        tool="web_search",
        result=f"{len(results)} results",
    )
    return results


@tool
async def scrape_url(url: str) -> dict[str, Any]:
    """
    Scrape a URL with crawl4ai and return its content as markdown.

    Args:
        url: The absolute URL to scrape.

    Returns:
        {"url", "title", "markdown"} — markdown is truncated to ~8000 chars to
        keep the agent context manageable. If scraping fails, returns
        {"url", "error"}.
    """
    events.emit("tool_call", stage="searcher", tool="scrape_url", args={"url": url})
    try:
        crawler = await _get_crawler()
        result = await crawler.arun(url=url)
    except Exception as e:  # noqa: BLE001
        log.exception("scrape_url failed for %s", url)
        events.emit("tool_error", stage="searcher", tool="scrape_url", error=str(e))
        return {"url": url, "error": f"{type(e).__name__}: {e}"}

    if not getattr(result, "success", False):
        events.emit(
            "tool_error",
            stage="searcher",
            tool="scrape_url",
            error=getattr(result, "error_message", "unknown"),
        )
        return {"url": url, "error": getattr(result, "error_message", "unknown scrape failure")}

    md = getattr(result, "markdown", "") or ""
    # crawl4ai may return a MarkdownGenerationResult object; normalize to string.
    if hasattr(md, "raw_markdown"):
        md = md.raw_markdown or ""
    md = str(md)
    truncated = md[:MAX_SCRAPE_CHARS]
    title = (getattr(result, "metadata", {}) or {}).get("title") or ""

    events.emit(
        "tool_result",
        stage="searcher",
        tool="scrape_url",
        result=f"{len(truncated)} chars from {url}",
    )
    return {
        "url": url,
        "title": title,
        "markdown": truncated,
        "truncated": len(md) > MAX_SCRAPE_CHARS,
    }


RESEARCH_TOOLS = [web_search, scrape_url]
