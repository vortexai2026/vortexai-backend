# app/services/daily_report.py
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal
from app.services.emailer import send_email

REPORT_EMAIL = os.getenv("REPORT_EMAIL")


async def send_daily_green_report(db: AsyncSession) -> int:
    if not REPORT_EMAIL:
        return 0

    res = await db.execute(select(Deal).where(Deal.profit_flag == "green").order_by(Deal.id.desc()))
    greens = list(res.scalars().all())

    if not greens:
        return 0

    lines = []
    for d in greens[:25]:
        lines.append(
            f"{d.id} | {d.address} | ${d.seller_price:,.0f} | ARV ${d.arv_estimated:,.0f} | "
            f"Repairs ${d.repair_estimate:,.0f} | MAO ${d.mao:,.0f} | Spread ${d.spread:,.0f} | {d.market_tag}"
        )

    subject = f"🔥 Green Deals Report ({len(greens)} total)"
    body = "Top Green Deals:\n\n" + "\n".join(lines)

    send_email(REPORT_EMAIL, subject, body)
    return len(greens)
