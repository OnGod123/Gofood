import os
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_message_with_openai(message: str):
    """
    Intelligent parser for WhatsApp or SMS messages.
    Returns structured JSON with intent and extracted fields.
    """
    schema = {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": [
                    "order_food", "check_balance", "wallet_credit",
                    "wallet_debit", "track_order", "help", "unknown"
                ]
            },
            "vendor": {"type": "string"},
            "items": {"type": "array", "items": {"type": "string"}},
            "amount": {"type": "number"},
            "sender_name": {"type": "string"},
            "reference": {"type": "string"}
        },
        "required": ["intent"]
    }

    prompt = f"""
You are a financial and food-order assistant.
Analyze the user's message and return a JSON following this structure:

{json.dumps(schema, indent=2)}

Examples:
1. Message: "I want to buy amala and ewedu from Iya Sukura"
   → {{ "intent": "order_food", "vendor": "Iya Sukura", "items": ["amala", "ewedu"] }}

2. Message: "My bank alert says ₦2000 credited from John Doe TRX111"
   → {{ "intent": "wallet_credit", "sender_name": "John Doe", "amount": 2000, "reference": "TRX111" }}

3. Message: "Check my balance"
   → {{ "intent": "check_balance" }}

Now parse this message and strictly return only valid JSON:
"{message}"
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        result_text = response.choices[0].message.content.strip()

        # Extract valid JSON safely
        start = result_text.find("{")
        end = result_text.rfind("}") + 1
        json_part = result_text[start:end]
        return json.loads(json_part)
    except Exception as e:
        return {"intent": "unknown", "error": str(e)}

