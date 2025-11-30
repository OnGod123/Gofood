import re
import json
import openai


def parse_items(text: str):
    """
    Simple parser:
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
            name = match.group(2).strip().lower()
        else:
            qty = 1
            name = p.lower()

        if name:
            out.append({"name": name, "qty": qty})

    return out


def ai_parse_items(text: str):
    """
    If simple parser fails → use OpenAI.
    """

    # Step 1: try simple parser
    items = parse_items(text)
    if items:
        return items

    # Step 2: fallback to OpenAI
    prompt = f"""
You are an intelligent order parser for WhatsApp messages.

Extract all items and quantities.

Rules:
- Return ONLY valid JSON.
- Each item is: {{ "name": <string>, "qty": <integer> }}
- If quantity missing, assume 1.
- Normalize item names to lowercase.
- Handle multiple items separated by commas, spaces, or newlines.

Input:
{text}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You extract food items."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )

        data = json.loads(response.choices[0].message.content)
        out = []
        for item in data:
            name = item.get("name", "").strip().lower()
            qty = int(item.get("qty", 1))
            if name:
                out.append({"name": name, "qty": qty})
        return out

    except Exception:
        return []



# ---------------------------
# 2. ADDRESS PARSERS
# ---------------------------

def parse_address(text: str):
    """
    Simple extraction:
    - Remove item-looking patterns (e.g. `2 shawarma`)
    - Return remaining text in lowercase.
    """
    # Remove patterns like "2 shawarma"
    cleaned = re.sub(r"\b\d+\s+\w+", "", text)
    cleaned = cleaned.strip().lower()

    # Very simple check: must contain at least 2 words to be an address
    if len(cleaned.split(" ")) >= 2:
        return cleaned

    return ""  # fail → fallback to AI



def ai_parse_address(text: str):
    """
    Fallback to OpenAI for address detection.
    """

    prompt = f"""
You are an address extraction assistant.

Extract only the DELIVERY ADDRESS from the message.

Rules:
- Return ONLY a raw string (no JSON, no explanation).
- Lowercase it.
- Remove anything that looks like an item or quantity.
- Must look like a real delivery address.

Input:
{text}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You extract delivery addresses."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )

        addr = response.choices[0].message.content.strip()
        return addr.lower()

    except Exception:
        return ""



def parse_vendor(text: str):
    """
    Simple vendor extraction:
    - vendor usually one word or two
    - lowercase
    """

    text = text.strip().lower()
    # vendor name should be short (1–3 words)
    parts = text.split(" ")

    if 1 <= len(parts) <= 3:
        return text

    return ""  # fail → fallback to AI



def ai_parse_vendor(text: str):
    """
    Use OpenAI to extract vendor name only.
    """

    prompt = f"""
Extract ONLY the vendor name from the text.

Rules:
- Vendor is a short name: 1–3 words.
- No items. No address.
- Lowercase.
- Output only the vendor name as plain text.

Input:
{text}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You extract vendor names."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )

        name = response.choices[0].message.content.strip()
        return name.lower()

    except Exception:
        return ""

