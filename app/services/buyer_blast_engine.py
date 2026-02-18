from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.buyer import Buyer
from app.models.deal import Deal
from app.services.lifecycle_control import set_status
from app.services.brevo_client import brevo_post


async def blast_buyers(db: AsyncSession, deal: Deal):
    stmt = select(Buyer).where(Buyer.state == deal.state)
    buyers = (await db.execute(stmt)).scalars().all()

    message = f"New Deal: {deal.address} | ARV: {deal.arv} | Asking: {deal.offer_price}"

    for buyer in buyers:
        if buyer.email:
            await brevo_post("/smtp/email", {
                "to": [{"email": buyer.email}],
                "sender": {"name": "Vortex AI", "email": "no-reply@yourdomain.com"},
                "subject": "New Investment Opportunity",
                "htmlContent": f"<p>{message}</p>"
            })

    await set_status(db, deal, "BLASTED")

    return {"buyers_notified": len(buyers)}
