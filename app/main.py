"""
FastMCP quickstart example.

This server demonstrates how to expose MCP tools and prompts for restaurant
order handling and call session management. It includes utilities to
initialize calls, manage customers, create and validate orders, and handle
greetings.

Run from the repository root:
    uv run examples/snippets/servers/fastmcp_quickstart.py
"""
import json
from mcp.server.fastmcp import FastMCP
from restaurants_tools import restaurant_tools
from pydantic import BaseModel, Field
from typing import List, Optional


# ==========================================================
# 🧩 Data Models
# ==========================================================

class Modifier(BaseModel):
    """
    Represents a modifier applied to an item (e.g., extra cheese, no onions).

    Attributes:
        is_active (bool): Whether the modifier is active.
        modifier_group_id (int): The group to which the modifier belongs.
        modifier_id (int): Unique ID of the modifier.
        name (str): Display name of the modifier.
        price_delta (float): Price difference added by this modifier.
        quantity (int): Quantity of this modifier applied.
    """
    modifier_group_id: int
    modifier_id: int
    name: str
    price_delta: float
    quantity: int
    is_active: bool


class Item(BaseModel):
    """
    Represents an item in a customer's order.

    Attributes:
        base_price (float): Base price of the item.
        item_id (int): Unique ID of the item.
        name (str): Name of the item.
        note (Optional[str]): Optional note or customization.
        options (List[dict]): List of selected options or configurations.
        modifiers (List[Modifier]): List of applied modifiers.
        price (float): Final calculated price for this item.
        quantity (int): Quantity of the item ordered.
    """

    item_id: int
    name: str
    base_price: float
    quantity: int
    note: Optional[str]
    modifiers: List[Modifier]
    options: List[dict]  = Field(default_factory=list, description="List of selected options or configurations")



class Order(BaseModel):
    """
    Represents an entire order for a restaurant.

    Attributes:
        language_code (str): Language code (e.g., 'en', 'ar').
        business_id (int): Unique business identifier.
        customer_id (int): Unique customer identifier.
        business_phone (str): Business phone number.
        customer_phone (str): Customer phone number.
        items (List[Item]): List of ordered items.
    """
    call_sid: str
    language_code: str
    business_phone: str
    customer_phone: str
    items: List[Item]


class CallInit(BaseModel):
    """
    Represents the initialization of a phone call session.

    Attributes:
        call_sid (str): Unique session identifier for the call.
        customer_id (str): Customer's unique identifier.
        customer_name (str): Full name of the customer.
        business_id (str): Business's unique identifier.
        business_name (str): Name of the business or restaurant.
        language (str): Preferred communication language for the call.
    """
    call_sid: str
    customer_id: str
    customer_name: str
    business_id: str
    business_name: str
    language: str


# ==========================================================
# ⚙️ MCP Server Setup
# ==========================================================

# Create an MCP server instance
mcp = FastMCP("Demo", json_response=True, host="0.0.0.0", port=7000)


# ==========================================================
# 📞 Call and Customer Tools
# ==========================================================

@mcp.tool()
def Initiate_call(business_phone: str, customer_phone: str, call_sid: str) -> CallInit:
    """
    Initiate the call and retrieve the CallInit structure.

    This tool initializes the session context for a phone call, linking
    the customer and business entities.

    Args:
        business_phone (str): The restaurant's phone number.
        customer_phone (str): The customer's phone number.
        call_sid (str): Unique call session ID (e.g., from Twilio).

    Returns:
        CallInit: Object containing call and participant details.
    """
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
    """
    Update the customer's name and details.

    Args:
        customer_id (str): Unique customer identifier.
        first_name (str): Customer's first name.
        last_name (str): Customer's last name.
    """
    return restaurant_tools.update_customer(customer_id, first_name, last_name)


@mcp.tool()
def update_customer_language(customer_id, language: str):
    """
    Update the customer's preferred language.

    Args:
        customer_id (str): Unique customer identifier.
        language (str): New language code (e.g., 'en', 'ar').
    """
    return restaurant_tools.update_customer_language(customer_id, language)


# ==========================================================
# 🧾 Order Management Tools
# ==========================================================

@mcp.tool()
def create_order(order: Order) -> dict:
    """
    Create a new restaurant order.

    This tool receives a structured order object from the AI assistant or an external system,
    ensures that the required identifiers and data fields are present, and then forwards
    the validated order to the underlying `restaurant_tools.create_order()` function
    for database persistence or further processing.

    Behavior:
        - Converts the input `Order` object (Pydantic model) to a dictionary for compatibility.
        - Hardcodes `customer_id` and `business_id` values for demonstration purposes.
          In this example, all orders are attributed to:
            • customer_id = 33  →  "Mamdouh"
            • business_id = 97  →  "Kaware3"
        - Iterates through all items in the order to ensure that each contains
          an `options` field. If missing, it automatically adds an empty list.
        - Forwards the normalized dictionary to the core restaurant order handler.

    Args:
        order (Order):
            A validated Pydantic `Order` model containing the following attributes:
            - language_code (str): Language of the order (e.g., "en", "ar").
            - business_id (int): Business ID (will be overridden).
            - customer_id (int): Customer ID (will be overridden).
            - business_phone (str): The restaurant’s phone number.
            - customer_phone (str): The customer’s phone number.
            - items (List[Item]): List of ordered items, each with pricing, modifiers, and notes.

    Returns:
        Any:
            The response returned by `restaurant_tools.create_order(order_dict)`, which may include
            a confirmation message, order identifier, or success indicator depending on implementation.

    Notes:
        - In a production deployment, `customer_id` and `business_id` should be dynamically resolved
          via the `Initiate_call` session context, not hardcoded.
        - This function currently acts as a preprocessor to guarantee
          order data integrity before persistence or downstream processing.
    """

    # Use model_dump() instead of dict()
    order_dict = order.model_dump() if hasattr(order, 'model_dump') else dict(order)

    # Hardcode customer_id and business_id
    order_dict['customer_id'] = 33
    order_dict['business_id'] = 97

    # Ensure all items have required fields
    if 'items' in order_dict:
        for item in order_dict['items']:
            if 'options' not in item:
                item['options'] = []

    return restaurant_tools.create_order(order_dict)


@mcp.tool()
def validate_order(order: Order) -> dict:
    """
    Validate order items and calculate totals.

    Checks for proper format and calls the restaurant tool for validation.

    Args:
        order (Order): The order data structure to validate.

    Returns:
        Validation results or error message if invalid.
    """
    # Convert Order object to dict and ensure customer_id is hardcoded
    # Use model_dump() instead of dict()
    order_dict = order.model_dump() if hasattr(order, 'model_dump') else dict(order)

    # Hardcode customer_id and business_id
    order_dict['customer_id'] = 33
    order_dict['business_id'] = 97

    # Ensure all items have required fields
    if 'items' in order_dict:
        for item in order_dict['items']:
            if 'options' not in item:
                item['options'] = []

    return restaurant_tools.validate_order(order_dict)


@mcp.tool()
def hangup_call() -> str:
    """
    End the call gracefully with a polite closing message.

    Returns:
        str: Confirmation that the call ended.
    """
    return "Call ended gracefully"

# ==========================================================
# 🚀 Server Entry Point
# ==========================================================

if __name__ == "__main__":
    """
    Entry point for running the MCP server.

    The server can operate in multiple transport modes.
    Currently using 'streamable-http' for testing via MCP Inspector.
    """
    import sys
    # mcp.run(transport="stdio")
    mcp.run(transport="streamable-http")
