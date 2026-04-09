"""
SMS Simulation Service — sends real phishing SMS via Twilio
"""
from backend.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

TEMPLATES = {
    "beginner": {
        "message": "DHL EXPRESS: Your parcel #78423 could not be delivered. Pay £1.99 redelivery fee: http://dhl-redeliver.info/pay or it will be returned. [PhishGuard Training]",
        "red_flags": [
            "Link goes to dhl-redeliver.info not the official dhl.com",
            "Legitimate DHL never asks for payment via an SMS link",
            "Small fee amount is used to lower your suspicion",
            "Creates urgency with threat of parcel being returned",
        ]
    },
    "intermediate": {
        "message": "HSBC ALERT: Unusual sign-in detected. Your card has been temporarily blocked. Verify now: http://hsbc-secure-verify.com/unblock [PhishGuard Training]",
        "red_flags": [
            "Link goes to hsbc-secure-verify.com not hsbc.co.uk",
            "Banks never send verification links via SMS",
            "Creates fear about a blocked card to force immediate action",
            "No personalisation — does not use your name or last 4 digits",
        ]
    },
    "advanced": {
        "message": "Hi it's the CEO. In back-to-back meetings — need you to buy 5x £200 Amazon gift cards for a client deal closing today. WhatsApp codes to +447700000123. Don't mention yet — surprise for team. [PhishGuard Training]",
        "red_flags": [
            "CEO gift card requests via SMS is a known Business Email Compromise scam",
            "Secrecy instruction prevents you from verifying with colleagues",
            "Urgency prevents you from thinking carefully",
            "Real executives never request gift cards via text message",
        ]
    }
}


def send_phishing_sms(to_phone: str, difficulty: str) -> dict:
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        return {"sent": False, "reason": "Twilio not configured"}

    if not to_phone or to_phone.strip() == "":
        return {"sent": False, "reason": "No phone number provided"}

    template = TEMPLATES.get(difficulty, TEMPLATES["beginner"])

    try:
        from twilio.rest import Client
        client  = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body  = template["message"],
            from_ = TWILIO_PHONE_NUMBER,
            to    = to_phone,
        )
        return {
            "sent":      True,
            "to":        to_phone,
            "sid":       message.sid,
            "preview":   template["message"][:80] + "...",
            "red_flags": template["red_flags"],
        }
    except Exception as e:
        return {"sent": False, "reason": str(e), "red_flags": template["red_flags"]}
