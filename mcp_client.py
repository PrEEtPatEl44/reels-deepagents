import os

from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_scrapegraph_tools():
    """
    Connect to the ScrapeGraph AI MCP server over stdio and return its tools.

    The server is launched via `uvx scrapegraph-mcp` — no Node dependency.
    If that entry-point name is wrong in a future release, try:
        command="uvx", args=["--from", "scrapegraph-mcp", "<script-name>"]

    Returns:
        (tools, client) — hold `client` alive for the lifetime of graph execution
        so the stdio child process isn't garbage-collected mid-run.
    """
    api_key = os.environ.get("SGAI_API_KEY")
    if not api_key:
        raise RuntimeError("SGAI_API_KEY is not set — copy .env.example to .env and fill it in.")

    client = MultiServerMCPClient(
        {
            "scrapegraph": {
                "transport": "stdio",
                "command": "uvx",
                "args": ["scrapegraph-mcp"],
                "env": {"SGAI_API_KEY": api_key},
            }
        }
    )
    tools = await client.get_tools()
    return tools, client
