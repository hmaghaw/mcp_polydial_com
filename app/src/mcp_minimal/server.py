"""
Minimal MCP Server — no 3rd-party dependencies.
Runs a simple arithmetic and echo tool for testing.
"""

from mcp.server.fastmcp import FastMCP

# Create MCP app
mcp = FastMCP("Minimal MCP Server", json_response=True, host="0.0.0.0", port=7000)

@mcp.tool()
def echo(text: str) -> str:
    """
    Return the same text back to the client.
    """
    return f"Echo: {text}"

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers and return the result.
    """
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers and return the result.
    """
    return a * b

def main():
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
