import os
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.models.deal import Deal
from app.models.buyer import Buyer


BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")
FROM_NAME = os.getenv("FROM_NAME", "Vortex AI")


async def send_email(to_email: str, subject: str, html_content: str):
    if not BREVO_API_KEY:
        print("⚠ BREVO_API_KEY missing — skipping email")
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

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)


async def notify_buyer_matched(db: AsyncSession, buyer: Buyer, deal: Deal):
    subject = f"🔥 New Deal Matched: {deal.title}"

    html = f"""
    <h2>New Deal Matched</h2>
    <p><strong>Title:</strong> {deal.title}</p>
    <p><strong>City:</strong> {deal.city}</p>
    <p><strong>Price:</strong> ${deal.price}</p>
    <p><strong>Expected Profit:</strong> ${deal.expected_profit}</p>
    """

    await send_email(buyer.email, subject, html)
