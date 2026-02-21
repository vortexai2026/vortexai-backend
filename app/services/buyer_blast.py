# app/services/buyer_blast.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.buyer import Buyer
from app.models.deal import Deal
from app.services.emailer import send_email


async def blast_green_deals(db: AsyncSession, deal: Deal) -> int:
    """
    Sends a green deal to matching buyers.
    Returns number of emails sent.
    """

    # Basic buyer matching (expand later with match_engine if needed)
    result = await db.execute(
        select(Buyer).where(
            Buyer.is_active == True,
            Buyer.min_price <= deal.price,
            Buyer.max_price >= deal.price
        )
    )

    buyers = result.scalars().all()

    if not buyers:
        return 0

    emails_sent = 0

    for buyer in buyers:
        subject = f"🔥 New Green Deal in {deal.city}"

        body = f"""
        Hi {buyer.name},

        We have a GREEN deal that matches your buy box.

        Address: {deal.address}
        Price: ${deal.price}
        ARV: ${deal.arv}
        Estimated Repairs: ${deal.repairs}
        Estimated Profit: ${deal.estimated_profit}

        If interested, reply immediately.

        - Vortex AI
        """

        await send_email(
            to_email=buyer.email,
            subject=subject,
            body=body
        )

        emails_sent += 1

    return emails_sent
