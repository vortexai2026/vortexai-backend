# app/emailer.py

import os
import smtplib
from email.message import EmailMessage
from typing import Optional

"""
EMAILER MODULE
Used by AI Level 4 (Action AI)

If email credentials are not set, it will LOG instead of crashing.
"""

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)


def send_email(
    to_email: str,
    subject: str,
    body: str,
    html: Optional[str] = None
) -> bool:
    """
    Send an email safely.
    If SMTP is not configured, it logs instead of crashing the app.
    """

    # 🔒 Safety: do not crash system if email not configured
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print("⚠️ EMAIL NOT SENT (SMTP not configured)")
        print("To:", to_email)
        print("Subject:", subject)
        print("Body:", body)
        return False

    try:
        msg = EmailMessage()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        if html:
            msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print("❌ Email failed:", str(e))
        return False
