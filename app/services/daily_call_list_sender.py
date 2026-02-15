# app/services/daily_call_list_sender.py

import os
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.priority_engine import refresh_priorities
from app.services.daily_call_list import get_top_call_list, format_call_list_email
from app.services.emailer import send_email

async def send_daily_call_list(db: AsyncSession, top: int = 10):
    # Refresh priority first
    await refresh_priorities(db, limit=200)

    # Build list
    deals = await get_top_call_list(db, top=top)
    body = format_call_list_email(deals)

    to_email = os.getenv("DAILY_CALL_LIST_EMAIL")
    if not to_email:
        raise RuntimeError("DAILY_CALL_LIST_EMAIL env var missing")

    subject = "Vortex AI — Top Call List (Today)"

    send_email(to_email, subject, body)

    return {"sent_to": to_email, "top": top, "count": len(deals)}
