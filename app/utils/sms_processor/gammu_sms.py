import gammu

def send_sms(phone: str, text: str) -> bool:
    """
    Send SMS using Gammu modem.
    Returns True if sent, False otherwise.
    """
    try:
        sm = gammu.StateMachine()
        sm.ReadConfig()
        sm.Init()

        sm.SendSMS({
            "Text": text,
            "SMSC": {"Location": 1},
            "Number": phone
        })

        print(f"SMS sent to {phone}")
        return True

    except Exception as e:
        print("Gammu send_sms failed:", e)
        return False

