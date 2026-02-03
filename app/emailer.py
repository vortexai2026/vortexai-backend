import os
import requests

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "alerts@yourdomain.com")

if not BREVO_API_KEY:
    raise RuntimeError("BREVO_API_KEY is not set")


def send_email(to_email: str, subject: str, html_content: str):
    """
    Send email using Brevo (Sendinblue)
    """

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    payload = {
        "sender": {"email": BREVO_SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        raise Exception(f"Brevo error: {response.text}")

    return True
