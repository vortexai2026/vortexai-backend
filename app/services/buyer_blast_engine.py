from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.buyer import Buyer
from app.models.deal import Deal
from app.services.lifecycle_control import set_status
from app.services.brevo_client import brevo_post


async def match_buyers_for_deal(db: AsyncSession, deal: Deal):
    """
    Match buyers by state.
    You can improve this later by zip, asset type, etc.
    """
    stmt = select(Buyer).where(Buyer.state == deal.state)
    buyers = (await db.execute(stmt)).scalars().all()
    return buyers


def build_buyer_email(deal: Deal):
    """
    Build email content for buyer blast.
    """
    return f"""
    Investment Opportunity

    Address: {deal.address}
    ARV: {deal.arv}
    Offer Price: {deal.offer_price}

    Contact us for details.
    """


async def blast_buyers(db: AsyncSession, deal: Deal):
    buyers = await match_buyers_for_deal(db, deal)

    email_content = build_buyer_email(deal)

    for buyer in buyers:
        if buyer.email:
            await brevo_post("/smtp/email", {
                "to": [{"email": buyer.email}],
                "sender": {"name": "Vortex AI", "email": "no-reply@yourdomain.com"},
                "subject": "New Investment Deal",
                "htmlContent": f"<pre>{email_content}</pre>"
            })

    await set_status(db, deal, "BLASTED")

    return {"buyers_notified": len(buyers)}
