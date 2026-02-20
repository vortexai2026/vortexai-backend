from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.emailer import send_email   # ✅ FIXED IMPORT


async def blast_deal_to_buyers(db: AsyncSession, deal: Deal) -> dict:
    """
    Blast a GREEN deal to matching buyers
    """

    if deal.profit_flag != "green":
        return {"error": "Only green deals can be blasted"}

    # Match buyers by market + price
    result = await db.execute(
        select(Buyer).where(
            Buyer.market_tag == deal.market_tag,
            Buyer.max_price >= (deal.mao or deal.seller_price or 0)
        )
    )

    buyers = list(result.scalars().all())

    if not buyers:
        return {"buyers_matched": 0, "emails_sent": 0}

    subject = f"🔥 Off-Market Deal - {deal.address}"

    body = f"""
Deal: {deal.address}, {deal.city}, {deal.state} {deal.zip_code}

Seller Price: ${deal.seller_price:,.0f}
ARV: ${deal.arv_estimated:,.0f}
Repairs: ${deal.repair_estimate:,.0f}
MAO: ${deal.mao:,.0f}
Spread: ${deal.spread:,.0f}
Confidence: {deal.confidence_score}
Flag: {deal.profit_flag}

Reply with: INTERESTED + Proof of Funds.
"""

    emails_sent = 0

    for buyer in buyers:
        if buyer.email:
            send_email(buyer.email, subject, body)
            emails_sent += 1

    return {
        "buyers_matched": len(buyers),
        "emails_sent": emails_sent
    }
