from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ai_level2_scoring import score_pending_deals
from app.ai.ai_daily_report import send_daily_green_report

async def run_level7_cycle(db: AsyncSession) -> dict:
    """
    Level 7 cycle:
    1) score pending deals (adds ARV/flag)
    2) send green daily report (last 24h)
    """
    scored = await score_pending_deals(db, limit=50)
    sent = await send_daily_green_report(db)

    greens = [d for d in scored if d.profit_flag == "green"]
    oranges = [d for d in scored if d.profit_flag == "orange"]
    reds = [d for d in scored if d.profit_flag == "red"]

    return {
        "scored_total": len(scored),
        "scored_green": len(greens),
        "scored_orange": len(oranges),
        "scored_red": len(reds),
        "daily_email_sent_count": sent,
    }
