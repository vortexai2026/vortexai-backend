# app/services/daily_call_list.py

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal

async def get_top_call_list(db: AsyncSession, top: int = 10):
    q = (
        select(Deal)
        .where(Deal.status.in_(["GREEN", "CONTACTED", "FOLLOW_UP", "OFFER_SENT", "UNDER_CONTRACT", "NEW"]))
        .order_by(desc(Deal.priority_score), desc(Deal.id))
        .limit(top)
    )
    res = await db.execute(q)
    return res.scalars().all()

def format_call_list_email(deals):
    lines = []
    lines.append("Vortex AI — Top Call List (Today)\n")
    for i, d in enumerate(deals, start=1):
        lines.append(
            f"{i}) Deal #{d.id} | {d.status} | Priority: {d.priority_score}\n"
            f"   Title: {d.title}\n"
            f"   City: {d.city} | Price: {d.price}\n"
            f"   Reason: {d.priority_reason}\n"
        )
    return "\n".join(lines)
