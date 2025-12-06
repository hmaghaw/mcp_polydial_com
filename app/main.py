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

    order_dict = order.dict() if hasattr(order, 'dict') else dict(order)

    # Hardcode customer_id and business_id
    order_dict['customer_id'] = 33  # Always hardcode to 33 for Mamdouh
    order_dict['business_id'] = 97  # Hardcode business_id for Kaware3

    # Ensure all items have required fields
    if 'items' in order_dict:
        for item in order_dict['items']:
            if 'options' not in item:
                item['options'] = []  # Add empty options list if missing

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
    order_dict = order.dict() if hasattr(order, 'dict') else dict(order)

    # Hardcode customer_id and business_id
    order_dict['customer_id'] = 33  # Always hardcode to 33 for Mamdouh
    order_dict['business_id'] = 97  # Hardcode business_id for Kaware3

    # Ensure all items have required fields
    if 'items' in order_dict:
        for item in order_dict['items']:
            if 'options' not in item:
                item['options'] = []  # Add empty options list if missing

    # Call restaurant tool validation
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
# 🌐 Resources and Prompts
# ==========================================================

# Example specifying metadata
@mcp.resource(
    uri="data://app-status",      # Explicit URI (required)
    name="ApplicationStatus",     # Custom name
    description="Provides the current status of the application.", # Custom description
    mime_type="application/json"
)
def get_application_status() -> dict:
    """Internal function description (ignored if description is provided above)."""
    return {"status": "ok", "uptime": 12345, "version": mcp.settings.version} # Example usage

@mcp.resource(
    uri="data://app-status-01",      # Explicit URI (required)
    name="ApplicationStatus01",     # Custom name
    description="Provides the current status of the application 01.", # Custom description
    mime_type="text/plain"
)
def get_application_status_01() -> dict:
    """Internal function description (ignored if description is provided above)."""
    return "Thank you"# Example usage

@mcp.resource(
    uri="data://menu/{business_id}",      # Explicit URI (required)
    name="RestaurantMenu",     # Custom name
    description="Provides the current status of the application 01.", # Custom description
    mime_type="application/json"
)
def get_menu(business_id:str) -> dict:
    """Internal function description (ignored if description is provided above)."""
    menu = get_business_menu(business_id)
    return menu


@mcp.resource(
    uri="greet://person/{name}",      # Explicit URI (required)
    name="GreetingName",     # Custom name
    description="Providesgreeting of the application 01.", # Custom description
    mime_type="text/plain"
)
def get_greeting(name: str) -> str:
    """
    Retrieve a personalized greeting message.

    Args:
        name (str): The name to include in the greeting.

    Returns:
        str: Personalized greeting text.
    """
    return f"Hello, {name}! this is a greeting!"


@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """
    Generate a greeting prompt message.

    Args:
        name (str): Person's name to greet.
        style (str): Greeting style ('friendly', 'formal', or 'casual').

    Returns:
        str: Natural language instruction for the model to generate a greeting.
    """
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

def get_business_menu(business_id:str) -> dict:
    return {
  "categories" : [ "إضافات", "فطور", "الكلاسيكيات", "حلويات", "غمسات ومقبلات", "مشروبات", "الأطباق الرئيسية", "مشوي", "أطفال", "سلطات", "ساندويتشات", "مقبلات" ],
  "menu" : [ {
    "category" : "إضافات",
    "items" : [ {
      "name" : "خبز بلدي",
      "original_name" : "Balady Bread",
      "description" : "",
      "original_description" : "",
      "base_price" : 3.0,
      "item_id" : 1137,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "فتوش",
      "original_name" : "Fattoush",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.0,
      "item_id" : 1182,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "فول مدمس",
      "original_name" : "Ful Madames",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.5,
      "item_id" : 1141,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "فخذ خروف فقط",
      "original_name" : "Just Lamb Shank",
      "description" : "",
      "original_description" : "",
      "base_price" : 18.0,
      "item_id" : 1134,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ملوخية فقط",
      "original_name" : "Just Molokheya",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.5,
      "item_id" : 1135,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كباب (4 قطع)",
      "original_name" : "Kobeba (4pcs)",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.0,
      "item_id" : 1142,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "أرز مصراوي مع شعرية",
      "original_name" : "Masrawy Rice w/ Sha3reya",
      "description" : "",
      "original_description" : "",
      "base_price" : 6.0,
      "item_id" : 1143,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "سلطة مصراوي",
      "original_name" : "Masrawy Salata",
      "description" : "",
      "original_description" : "",
      "base_price" : 14.0,
      "item_id" : 1181,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "بطاطس مقلية متبلة مصراوي",
      "original_name" : "Masrawy Seasoned Fries",
      "description" : "",
      "original_description" : "",
      "base_price" : 7.0,
      "item_id" : 1138,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "شرائح خبز البيتا",
      "original_name" : "Pita Chips",
      "description" : "",
      "original_description" : "",
      "base_price" : 2.5,
      "item_id" : 1136,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "سجق لحم بقري متبل",
      "original_name" : "Spiced Beef Sausage",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.5,
      "item_id" : 1139,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "طعمية (3 قطع)",
      "original_name" : "Tamaaya (3pcs)",
      "description" : "",
      "original_description" : "",
      "base_price" : 8.0,
      "item_id" : 1140,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "فطور",
    "items" : [ {
      "name" : "بسطرمة بلدي",
      "original_name" : "Basterma Balady",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.25,
      "item_id" : 1111,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش بيض وبسطرمة",
      "original_name" : "Eggs & Basterma Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.0,
      "item_id" : 1110,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "افطار مصراوي الكبير",
      "original_name" : "Masrawy Grand Breakfast",
      "description" : "",
      "original_description" : "",
      "base_price" : 40.0,
      "item_id" : 1106,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "على النيل",
      "original_name" : "On the Nile",
      "description" : "",
      "original_description" : "",
      "base_price" : 19.5,
      "item_id" : 1109,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "صباح الخير",
      "original_name" : "Saba7 El-Kher",
      "description" : "",
      "original_description" : "",
      "base_price" : 18.5,
      "item_id" : 1108,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "حلوى كليوباترا",
      "original_name" : "Sweet Cleopatra",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.25,
      "item_id" : 1107,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "الكلاسيكيات",
    "items" : [ {
      "name" : "بانيه دجاج",
      "original_name" : "Chicken Panne",
      "description" : "",
      "original_description" : "",
      "base_price" : 19.0,
      "item_id" : 1162,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "سمك الحدوق والبطاطس",
      "original_name" : "Haddock & Chips",
      "description" : "",
      "original_description" : "",
      "base_price" : 19.0,
      "item_id" : 1158,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "حمام محشي",
      "original_name" : "Hamam Mahshy",
      "description" : "",
      "original_description" : "",
      "base_price" : 42.5,
      "item_id" : 1160,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كبدة إسكندراني",
      "original_name" : "Kebda Eskandarani",
      "description" : "",
      "original_description" : "",
      "base_price" : 18.5,
      "item_id" : 1157,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كشري",
      "original_name" : "Koshary",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.5,
      "item_id" : 1163,
      "modifiers" : [ {
        "name" : "بصل مقرمش",
        "original_name" : "Crispy Onions",
        "price_delta" : 3.0,
        "group_name" : "إضافات كشري",
        "original_group_name" : "Koshary Add-ons",
        "is_required" : False,
        "modifier_id" : 377,
        "modifier_group_id" : 131
      }, {
        "name" : "حمص",
        "original_name" : "Hommos",
        "price_delta" : 2.5,
        "group_name" : "إضافات كشري",
        "original_group_name" : "Koshary Add-ons",
        "is_required" : False,
        "modifier_id" : 379,
        "modifier_group_id" : 131
      }, {
        "name" : "كمالة",
        "original_name" : "Kemala",
        "price_delta" : 7.0,
        "group_name" : "إضافات كشري",
        "original_group_name" : "Koshary Add-ons",
        "is_required" : False,
        "modifier_id" : 380,
        "modifier_group_id" : 131
      }, {
        "name" : "صلصة طماطم",
        "original_name" : "Tomato Souce",
        "price_delta" : 2.0,
        "group_name" : "إضافات كشري",
        "original_group_name" : "Koshary Add-ons",
        "is_required" : False,
        "modifier_id" : 378,
        "modifier_group_id" : 131
      } ],
      "options" : [ ]
    }, {
      "name" : "مكرونة بشاميل",
      "original_name" : "Macarona Béchamel",
      "description" : "",
      "original_description" : "",
      "base_price" : 18.0,
      "item_id" : 1161,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "فيوجن مصراوي",
      "original_name" : "Masrawy Fusion",
      "description" : "",
      "original_description" : "",
      "base_price" : 18.0,
      "item_id" : 1159,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "حلويات",
    "items" : [ {
      "name" : "بسبوسة مصراوي",
      "original_name" : "Basbusa Masrawy",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.25,
      "item_id" : 1129,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "فطير مشلتت كامل",
      "original_name" : "Full Feteer",
      "description" : "",
      "original_description" : "",
      "base_price" : 29.0,
      "item_id" : 1124,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كنافة",
      "original_name" : "Kunafa",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.25,
      "item_id" : 1128,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "أم علي",
      "original_name" : "Om Ali",
      "description" : "",
      "original_description" : "",
      "base_price" : 14.5,
      "item_id" : 1127,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "رز باللبن",
      "original_name" : "Roz Bel Laban",
      "description" : "",
      "original_description" : "",
      "base_price" : 6.75,
      "item_id" : 1130,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "زلابية (12 قطعة)",
      "original_name" : "Zalabia (12pcs)",
      "description" : "",
      "original_description" : "",
      "base_price" : 11.0,
      "item_id" : 1126,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "زلابية (20 قطعة)",
      "original_name" : "Zalabia (20pcs)",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.5,
      "item_id" : 1125,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "غمسات ومقبلات",
    "items" : [ {
      "name" : "بابا غنوج",
      "original_name" : "Baba Ganoush",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.5,
      "item_id" : 1194,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "بصارة",
      "original_name" : "Besara",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.5,
      "item_id" : 1193,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "جمبري مقلي",
      "original_name" : "Breaded Shrimp",
      "description" : "",
      "original_description" : "",
      "base_price" : 16.5,
      "item_id" : 1189,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كالاماري حار",
      "original_name" : "Calamari with a Kick",
      "description" : "",
      "original_description" : "",
      "base_price" : 18.5,
      "item_id" : 1190,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "طبق الشيف",
      "original_name" : "Chef's Platter",
      "description" : "",
      "original_description" : "",
      "base_price" : 27.0,
      "item_id" : 1192,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "حمص كلاسيكي",
      "original_name" : "Classic Hummus",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.0,
      "item_id" : 1195,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "لفائف ملفوف فقط",
      "original_name" : "Just Cabbage Rolls",
      "description" : "",
      "original_description" : "",
      "base_price" : 14.0,
      "item_id" : 1184,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ورق عنب فقط",
      "original_name" : "Just Wara 3enab",
      "description" : "",
      "original_description" : "",
      "base_price" : 14.0,
      "item_id" : 1183,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "طبق صغير للشيف",
      "original_name" : "Mini Chef’s Platter",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.0,
      "item_id" : 1191,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "خلطة محشي",
      "original_name" : "Mix Mahashy",
      "description" : "",
      "original_description" : "",
      "base_price" : 16.0,
      "item_id" : 1185,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ممبرة",
      "original_name" : "Mombar",
      "description" : "",
      "original_description" : "",
      "base_price" : 15.0,
      "item_id" : 1188,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "مُسقعة مصرية",
      "original_name" : "Mussaka Masri",
      "description" : "",
      "original_description" : "",
      "base_price" : 12.5,
      "item_id" : 1186,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ممبرة مفردة",
      "original_name" : "Single Mombar",
      "description" : "",
      "original_description" : "",
      "base_price" : 4.0,
      "item_id" : 1187,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "مشروبات",
    "items" : [ {
      "name" : "مشروبات معبأة",
      "original_name" : "Bottled Drinks",
      "description" : "",
      "original_description" : "",
      "base_price" : 4.0,
      "item_id" : 1122,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "مشروبات غازية معلبة",
      "original_name" : "Canned Pop",
      "description" : "",
      "original_description" : "",
      "base_price" : 2.5,
      "item_id" : 1123,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كابتشينو / لاتيه",
      "original_name" : "Cappuccino / Latte",
      "description" : "",
      "original_description" : "",
      "base_price" : 4.0,
      "item_id" : 1114,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "قهوة / شاي",
      "original_name" : "Coffee / Tea",
      "description" : "",
      "original_description" : "",
      "base_price" : 3.5,
      "item_id" : 1117,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "إسبريسو / أمريكانو",
      "original_name" : "Espresso / Americano",
      "description" : "",
      "original_description" : "",
      "base_price" : 4.0,
      "item_id" : 1115,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "عصائر طازجة",
      "original_name" : "Fresh Juices",
      "description" : "",
      "original_description" : "",
      "base_price" : 0.0,
      "item_id" : 1120,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "شيكولاتة ساخنة / موكا",
      "original_name" : "Hot Chocolate / Mocha",
      "description" : "",
      "original_description" : "",
      "base_price" : 3.5,
      "item_id" : 1113,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "مشروبات مستوردة",
      "original_name" : "Imported Drinks",
      "description" : "",
      "original_description" : "",
      "base_price" : 5.0,
      "item_id" : 1119,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "مياه مصراوي",
      "original_name" : "Masrawy Water",
      "description" : "",
      "original_description" : "",
      "base_price" : 2.0,
      "item_id" : 1121,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "قهوة محمد صلاح",
      "original_name" : "Mo Salah Coffee",
      "description" : "",
      "original_description" : "",
      "base_price" : 4.5,
      "item_id" : 1112,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "إبريق الشاي",
      "original_name" : "Tea Pot",
      "description" : "",
      "original_description" : "",
      "base_price" : 10.0,
      "item_id" : 1116,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "قهوة تركي",
      "original_name" : "Turkish Coffee",
      "description" : "",
      "original_description" : "",
      "base_price" : 5.5,
      "item_id" : 1118,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "الأطباق الرئيسية",
    "items" : [ {
      "name" : "فتة كوارع",
      "original_name" : "Cow Feet Fatta",
      "description" : "",
      "original_description" : "",
      "base_price" : 21.0,
      "item_id" : 1152,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "هواوشي",
      "original_name" : "Hawawoshi",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.0,
      "item_id" : 1154,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "فتة فخذ خروف",
      "original_name" : "Lamb Shank Fatta",
      "description" : "",
      "original_description" : "",
      "base_price" : 25.0,
      "item_id" : 1151,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ملوخية ماما",
      "original_name" : "Mama's Molekheya",
      "description" : "",
      "original_description" : "",
      "base_price" : 16.5,
      "item_id" : 1155,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "بامية بلحم",
      "original_name" : "Okra w Beef",
      "description" : "",
      "original_description" : "",
      "base_price" : 23.0,
      "item_id" : 1153,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "سمك دنيس مع ردة",
      "original_name" : "Sea Bass w Rada",
      "description" : "",
      "original_description" : "",
      "base_price" : 33.0,
      "item_id" : 1156,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "مشوي",
    "items" : [ {
      "name" : "كباب لحم بقري",
      "original_name" : "Beef Kabab",
      "description" : "",
      "original_description" : "",
      "base_price" : 26.0,
      "item_id" : 1148,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "تيكا دجاج",
      "original_name" : "Chicken Tikka",
      "description" : "",
      "original_description" : "",
      "base_price" : 25.0,
      "item_id" : 1149,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كفتة مصرية",
      "original_name" : "Egyptian Kofta",
      "description" : "",
      "original_description" : "",
      "base_price" : 19.0,
      "item_id" : 1150,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "قطع لحم خروف",
      "original_name" : "Lamb Chops",
      "description" : "",
      "original_description" : "",
      "base_price" : 28.0,
      "item_id" : 1147,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "كباب لحم",
      "original_name" : "Lamb Kabab",
      "description" : "",
      "original_description" : "",
      "base_price" : 25.0,
      "item_id" : 1146,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "مشاوي مختلطة مصراوي",
      "original_name" : "Masrawy Mixed Grill",
      "description" : "",
      "original_description" : "",
      "base_price" : 90.0,
      "item_id" : 1144,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "شيش طاووق مصراوي",
      "original_name" : "Masrawy Shish Tawouk",
      "description" : "",
      "original_description" : "",
      "base_price" : 22.0,
      "item_id" : 1145,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "أطفال",
    "items" : [ {
      "name" : "كفتة كيمو",
      "original_name" : "Kimo's Kofta",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.0,
      "item_id" : 1132,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "خاص لولو",
      "original_name" : "Lulu's Special",
      "description" : "",
      "original_description" : "",
      "base_price" : 11.0,
      "item_id" : 1133,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "بانيه صغيرة",
      "original_name" : "Petite Panne",
      "description" : "",
      "original_description" : "",
      "base_price" : 14.0,
      "item_id" : 1131,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "سلطات",
    "items" : [ {
      "name" : "سلطة جرجير",
      "original_name" : "Arugula Salad",
      "description" : "",
      "original_description" : "",
      "base_price" : 16.0,
      "item_id" : 1180,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "فتوش",
      "original_name" : "Fattoush",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.0,
      "item_id" : 1182,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "سلطة مصراوي",
      "original_name" : "Masrawy Salata",
      "description" : "",
      "original_description" : "",
      "base_price" : 14.0,
      "item_id" : 1181,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "ساندويتشات",
    "items" : [ {
      "name" : "ساندويتش كباب لحم بقري",
      "original_name" : "Beef Kabab Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 22.0,
      "item_id" : 1165,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش جمبري مقلي",
      "original_name" : "Breaded Shrimp Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.5,
      "item_id" : 1167,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش كالاماري",
      "original_name" : "Calamari Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 19.5,
      "item_id" : 1168,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش كفتة مصرية",
      "original_name" : "Egyptian Kofta Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.5,
      "item_id" : 1166,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش دجاج ماريلاند",
      "original_name" : "El Maryland Chicken Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.0,
      "item_id" : 1172,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش فول",
      "original_name" : "Ful Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 7.5,
      "item_id" : 1176,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش سمك الحدوق",
      "original_name" : "Haddock Filet Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.0,
      "item_id" : 1173,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش كبدة",
      "original_name" : "Kebda Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 18.0,
      "item_id" : 1169,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش كباب لحم",
      "original_name" : "Lamb Kabab Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 21.0,
      "item_id" : 1164,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش فيوجن مصراوي",
      "original_name" : "Masrawy Fusion Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 15.0,
      "item_id" : 1171,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش باذنجان مخلل",
      "original_name" : "Pickled Eggplant Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 11.0,
      "item_id" : 1170,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش سجق لحم بقري متبل",
      "original_name" : "Spiced Beef Sausage Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 15.75,
      "item_id" : 1174,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "ساندويتش طعمية",
      "original_name" : "Tamaaya Sandwich",
      "description" : "",
      "original_description" : "",
      "base_price" : 8.5,
      "item_id" : 1175,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  }, {
    "category" : "مقبلات",
    "items" : [ {
      "name" : "شوربة عدس",
      "original_name" : "3ats Lentil Soup",
      "description" : "",
      "original_description" : "",
      "base_price" : 9.0,
      "item_id" : 1179,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "شوربة كوارع",
      "original_name" : "Kaware3 Cow Feet Soup",
      "description" : "",
      "original_description" : "",
      "base_price" : 17.0,
      "item_id" : 1178,
      "modifiers" : [ ],
      "options" : [ ]
    }, {
      "name" : "شوربة لسان عصفور",
      "original_name" : "Lesan Asfour Chicken Soup",
      "description" : "",
      "original_description" : "",
      "base_price" : 13.0,
      "item_id" : 1177,
      "modifiers" : [ ],
      "options" : [ ]
    } ]
  } ],
  "language" : "ar"
}
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
