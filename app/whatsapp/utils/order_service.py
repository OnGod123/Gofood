from app.database import db
from app.database.models import FoodItem, OrderSingle, OrderMultiple
import re
import openai

# Make sure to set your OpenAI API key in environment variables
# export OPENAI_API_KEY="your_api_key"

def parse_items(text: str):
    """
    Simple string parser:
    '2 shawarma, 1 burger' -> [{'name':'shawarma','qty':2}, ...]
    """
    out = []
    parts = re.split(r',|\n', text)
    for p in parts:
        p = p.strip()
        if not p:
            continue
        match = re.match(r"(\d+)\s+(.+)", p)
        if match:
            qty = int(match.group(1))
            name = match.group(2).strip()
        else:
            qty = 1
            name = p
        if name:
            out.append({"name": name, "qty": qty})
    return out

def ai_parse_items(text: str):
    """
    Hybrid parser: string parsing + OpenAI fallback
    """
    # Step 1: Try simple string parsing
    items = parse_items(text)
    if items:
        return items

    # Step 2: Use OpenAI GPT to intelligently parse messy input
    prompt = f"""
You are an intelligent order parser for WhatsApp messages.
Extract all food items and quantities in a list of dictionaries with 'name' and 'qty'.

Rules:
- If quantity is missing, assume 1
- Handle multiple items, separated by commas, newlines, or spaces
- Normalize names by stripping extra spaces
- Ignore invalid/empty entries

Return only valid JSON.

Input:
{text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an assistant that extracts food orders."},
                  {"role": "user", "content": prompt}],
        temperature=0
    )

    # Extract JSON from the model's output
    import json
    try:
        ai_output = response.choices[0].message.content.strip()
        # Ensure it's valid JSON
        parsed = json.loads(ai_output)
        normalized = []
        for it in parsed:
            name = it.get("name") or ""
            qty = int(it.get("qty", 1))
            if name:
                normalized.append({"name": name, "qty": qty})
        return normalized
    except Exception as e:
        # fallback if AI fails
        return []

def validate_items(vendor_id: int, items):
    validated = []
    for it in items:
        name = it["name"]
        qty = int(it.get("qty", 1))

        product = FoodItem.query.filter(
            FoodItem.vendor_id == vendor_id,
            FoodItem.item_name.ilike(f"%{name}%")
        ).first()

        if not product:
            return False, []

        validated.append({
            "product_id": product.id,
            "name": product.item_name,
            "qty": qty,
            "price": product.price
        })

    return True, validated

def build_order(user_id, vendor_name, items, address):
    if len(items) == 1:
        i = items[0]
        order = OrderSingle(
            user_id=user_id,
            vendor_name=vendor_name,
            product_name=i["name"],
            item_data=i,
            total=i["qty"] * i["price"],
            reciepient_address=address
        )
        db.session.add(order)
        db.session.commit()
        return order
    else:
        total = sum(i["qty"] * i["price"] for i in items)
        order = OrderMultiple(
            user_id=user_id,
            vendor_name=vendor_name,
            items_data=items,
            total=total,
            reciepient_address=address
        )
        db.session.add(order)
        db.session.commit()
        return order

