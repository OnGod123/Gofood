from app.utils.ai_parser import parse_message_with_openai

def process_incoming_whatsapp_message(value, message):
    text_body = message['text']['body'].strip()
    from_number = message['from']
    phone_number_id = value['metadata']['phone_number_id']

    parsed = parse_message_with_openai(text_body)
    intent = parsed.get("intent", "unknown")

    if intent == "order_food":
        vendor = parsed.get("vendor", "unknown vendor")
        items = ", ".join(parsed.get("items", []))
        reply = f"Got it! You want to order from *{vendor}*:\n🛒 {items}\n\nConfirm your order ✅"
    elif intent == "check_balance":
        reply = "Your wallet balance is ₦1,200.00"
    elif intent == "wallet_credit":
        sender = parsed.get("sender_name", "Unknown")
        amt = parsed.get("amount", 0)
        reply = f"Received ₦{amt:,.2f} from {sender}. Your wallet has been credited ✅"
    elif intent == "track_order":
        reply = "Your order is on the way 🚴"
    else:
        reply = "Sorry, I couldn’t understand your message. Try again."

    send_whatsapp_reply(phone_number_id, from_number, reply)

