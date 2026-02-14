import os
import httpx

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@vortexai.com")
FROM_NAME = os.getenv("FROM_NAME", "Vortex AI")


async def send_email(to_email: str, subject: str, html_content: str):
    """
    Safe email sender using Brevo.
    If no API key is set, it logs instead of crashing.
    """

    if not BREVO_API_KEY:
        print(f"[EMAIL SKIPPED] {to_email} | {subject}")
        return

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": FROM_NAME,
            "email": FROM_EMAIL
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

        if response.status_code >= 400:
            print("❌ Email failed:", response.text)
        else:
            print("✅ Email sent:", to_email)
