# app/services/emailer.py

import os
import smtplib
from email.message import EmailMessage
from typing import Optional, List, Tuple

# attachments: List[(filename, bytes, mimetype)]
Attachment = Tuple[str, bytes, str]

def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[Attachment]] = None
):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    from_email = os.getenv("FROM_EMAIL", user)

    if not host or not user or not password or not from_email:
        raise RuntimeError("SMTP env vars missing: SMTP_HOST/SMTP_USER/SMTP_PASS/FROM_EMAIL")

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachments:
        for filename, content_bytes, mimetype in attachments:
            maintype, subtype = mimetype.split("/", 1)
            msg.add_attachment(
                content_bytes,
                maintype=maintype,
                subtype=subtype,
                filename=filename
            )

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
