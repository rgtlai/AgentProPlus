"""
Example MCP server exposing two simple tools via stdio using FastMCP.

Run:
    python mcp_server.py

Then configure ReactAgent with:
    mcp_config=[{"id": "example", "command": "python", "args": ["mcp_server.py"]}]
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("example-tools")


@mcp.tool()
def echo(text: str) -> str:
    """Echo the provided text."""
    return text


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


if __name__ == "__main__":
    mcp.run()

