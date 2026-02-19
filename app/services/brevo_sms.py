import os
import httpx

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SMS_SENDER = os.getenv("BREVO_SMS_SENDER", "VortexAuto")

class BrevoSMS:
    BASE = "https://api.brevo.com/v3"

    @staticmethod
    async def send_sms(to_phone_e164: str, text: str) -> dict:
        if not BREVO_API_KEY:
            raise RuntimeError("Missing BREVO_API_KEY")
        headers = {"api-key": BREVO_API_KEY, "Content-Type": "application/json"}
        payload = {
            "sender": BREVO_SMS_SENDER,
            "recipient": to_phone_e164,
            "content": text,
            "type": "transactional",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(f"{BrevoSMS.BASE}/transactionalSMS/sms", headers=headers, json=payload)
            r.raise_for_status()
            return r.json()
