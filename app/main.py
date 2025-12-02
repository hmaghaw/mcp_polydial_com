"""
FastMCP quickstart example.

Run from the repository root:
    uv run examples/snippets/servers/fastmcp_quickstart.py
"""

from mcp.server.fastmcp import FastMCP
from restaurants_tools import restaurant_tools
from pydantic import BaseModel
from typing import List, Optional

class Modifier(BaseModel):
    is_active: bool
    modifier_group_id: int
    modifier_id: int
    name: str
    price_delta: float
    quantity: int

class Item(BaseModel):
    base_price: float
    item_id: int
    name: str
    note: Optional[str] = ""
    options: List[dict]
    modifiers: List[Modifier]
    price: float
    quantity: int

class Order(BaseModel):
    language_code: str
    business_id: int
    customer_id: int
    business_phone: str
    customer_phone: str
    items: List[Item]
# Create an MCP server
mcp = FastMCP("Demo", json_response=True, host="0.0.0.0", port=7000)

@mcp.tool()
def validate_order(order: Order):
    """Validate order items and calculate totals."""
    # This is a simplified version - you might want to implement more robust validation
    if not isinstance(order, dict) or 'items' not in order:
        return "Error: Invalid order format. Expected a dictionary with an 'items' key."
    return restaurant_tools.validate_order(order)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def greet_customer(customer_first_name: str) -> str:
    """Greet customer with his name"""
    return f"Hi {customer_first_name}, How are you?"

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# Run with streamable HTTP transport
if __name__ == "__main__":
    # Allow both transports
    import sys
    #mcp.run(transport="stdio")
    mcp.run(transport="streamable-http")