
import gammu

def send_sms(phone: str, text: str) -> bool:
    try:
        sm = gammu.StateMachine()
        sm.ReadConfig()
        sm.Init()

        message = {
            "Text": text,
            "SMSC": {"Location": 1},
            "Number": phone
        }
        sm.SendSMS(message)
        print(f"✅ SMS sent to {phone}")
        return True
    except Exception as e:
        print(f"❌ SMS sending failed: {e}")
        return False

