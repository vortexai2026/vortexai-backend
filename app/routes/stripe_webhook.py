import os
import stripe
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET missing")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    # We care about checkout completion
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        deal_id = session.get("metadata", {}).get("deal_id")
        amount_total = session.get("amount_total")  # cents
        payment_status = session.get("payment_status")  # paid / unpaid

        if deal_id:
            r = await db.execute(select(Deal).where(Deal.id == int(deal_id)))
            deal = r.scalar_one_or_none()
            if deal:
                deal.stripe_payment_status = "PAID" if payment_status == "paid" else "UNPAID"
                deal.paid_amount = (amount_total / 100.0) if amount_total else None
                deal.paid_at = datetime.utcnow()

                # Optional: If paid, you can move status to ASSIGNED (or keep ASSIGNED and just mark paid)
                # deal.status = "ASSIGNED"

                await db.commit()

    return {"received": True}
