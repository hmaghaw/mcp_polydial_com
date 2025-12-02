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

class CallInit(BaseModel):
    call_sid: str
    customer_id: str
    customer_name: str
    business_id: str
    business_name: str
    language: str

# Create an MCP server
mcp = FastMCP("Demo", json_response=True, host="0.0.0.0", port=7000)

@mcp.tool()
def Initiate_call( business_phone: str, customer_phone: str, call_sid: str) -> CallInit:

    """Initiate the call and retrieve the CallInit structure containing: customer_name, customerid and business_id"""
    result = CallInit(
        call_sid=call_sid,
        customer_id="33",
        customer_name="Mamdouh",
        business_id="97",
        business_name="Kaware3",
        language="en"
    )
    return result

@mcp.tool()
def update_customer(customer_id, first_name: str, last_name: str):
    """Update customer name and details."""
    return restaurant_tools.update_customer(customer_id, first_name, last_name)

@mcp.tool()
def update_customer_language(customer_id, language: str):
    """Update customer's preferred language."""
    return restaurant_tools.update_customer_language(customer_id, language)

@mcp.tool()
def create_order(order: Order):
    """Create a restaurant order."""
    return restaurant_tools.create_order(order)

@mcp.tool()
def validate_order(order: Order):
    """Validate order items and calculate totals."""
    # This is a simplified version - you might want to implement more robust validation
    if not isinstance(order, dict) or 'items' not in order:
        return "Error: Invalid order format. Expected a dictionary with an 'items' key."
    return restaurant_tools.validate_order(order)

@mcp.tool()
def hangup_call() -> str:
    """End call politely."""
    return "Call ended gracefully"

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