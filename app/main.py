import os
import requests

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")
FROM_NAME = os.getenv("FROM_NAME", "VortexAI")

def send_email(to_email: str, subject: str, html_content: str):
    """
    Brevo transactional email via API.
    If BREVO_API_KEY is missing, it will just log (safe).
    """
    if not BREVO_API_KEY:
        print(f"[EMAIL-SKIP] To={to_email} Subject={subject} (BREVO_API_KEY missing)")
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code >= 300:
            print("Brevo email error:", r.status_code, r.text)
    except Exception as e:
        print("Brevo email exception:", e)
