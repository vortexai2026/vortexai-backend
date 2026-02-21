import os
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.deal import Deal
import smtplib
from email.mime.text import MIMEText

REPORT_EMAIL = os.getenv("REPORT_EMAIL")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


async def send_green_report(db: AsyncSession):
    if not REPORT_EMAIL:
        return {"error": "REPORT_EMAIL not set"}

    result = await db.execute(
        select(Deal).where(Deal.status == "GREEN")
    )
    deals: List[Deal] = result.scalars().all()

    if not deals:
        return {"message": "No green deals"}

    body = "🔥 GREEN DEAL REPORT\n\n"

    for d in deals:
        body += f"""
Address: {d.address}
City: {d.city}
Price: {d.seller_price}
----------------------------------
"""

    msg = MIMEText(body)
    msg["Subject"] = "Vortex AI Green Deals"
    msg["From"] = EMAIL_USER
    msg["To"] = REPORT_EMAIL

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, REPORT_EMAIL, msg.as_string())

        return {"sent": len(deals)}

    except Exception as e:
        return {"error": str(e)}
