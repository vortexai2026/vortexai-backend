# app/services/buyer_blast.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.emailer import send_email


async def blast_deal_to_buyers(db: AsyncSession, deal: Deal) -> dict:
    if deal.profit_flag != "green":
        return {"error": "Only green deals can be blasted"}

    mao_price = float(deal.mao or deal.seller_price or 0)

    res = await db.execute(
        select(Buyer).where(
            Buyer.is_active == True,  # noqa: E712
            Buyer.market_tag == deal.market_tag,
            Buyer.max_price != None,  # noqa: E711
            Buyer.max_price >= mao_price,
        )
    )
    buyers = list(res.scalars().all())

    if not buyers:
        return {"buyers_matched": 0, "emails_sent": 0}

    subject = f"🔥 Off-Market Deal - {deal.address}"

    body = (
        f"Deal: {deal.address}, {deal.city}, {deal.state} {deal.zip_code}\n\n"
        f"Seller Price: ${deal.seller_price:,.0f}\n"
        f"ARV: ${deal.arv_estimated:,.0f}\n"
        f"Repairs: ${deal.repair_estimate:,.0f}\n"
        f"MAO: ${deal.mao:,.0f}\n"
        f"Spread: ${deal.spread:,.0f}\n"
        f"Confidence: {deal.confidence_score}\n"
        f"Flag: {deal.profit_flag}\n"
        f"Market: {deal.market_tag}\n\n"
        "Reply: INTERESTED + Proof of Funds.\n"
    )

    sent = 0
    for b in buyers:
        if b.email:
            send_email(b.email, subject, body)
            sent += 1

    return {"buyers_matched": len(buyers), "emails_sent": sent}
