import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.buyer import Buyer
from app.services.stripe_service import create_checkout_session

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.post("/checkout")
async def start_checkout(buyer_id: int, tier: str, db: AsyncSession = Depends(get_db)):
    # tier must be one of: free49, pro199, elite499
    if tier not in {"free49", "pro199", "elite499"}:
        raise HTTPException(status_code=400, detail="Invalid tier")

    res = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    buyer = res.scalar_one_or_none()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    app_url = os.getenv("APP_URL", "").rstrip("/")
    if not app_url:
        raise RuntimeError("APP_URL is missing in Railway Variables")

    success_url = f"{app_url}/billing/success"
    cancel_url = f"{app_url}/billing/cancel"

    session = create_checkout_session(
        buyer_email=buyer.email,
        tier=tier,
        success_url=success_url,
        cancel_url=cancel_url,
        buyer_id=buyer.id,
    )
    return {"checkout_url": session.url}

@router.get("/success")
async def billing_success():
    return {"ok": True, "message": "Payment successful. Subscription activating..."}

@router.get("/cancel")
async def billing_cancel():
    return {"ok": True, "message": "Checkout canceled."}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET missing")

    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig, webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    # We activate subscription on checkout completion
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        buyer_id = session.get("metadata", {}).get("buyer_id")
        tier = session.get("metadata", {}).get("tier")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        if buyer_id and tier:
            res = await db.execute(select(Buyer).where(Buyer.id == int(buyer_id)))
            buyer = res.scalar_one_or_none()
            if buyer:
                buyer.subscription_tier = tier
                buyer.is_active = True
                buyer.stripe_customer_id = customer_id
                buyer.stripe_subscription_id = subscription_id
                await db.commit()

    # Handle cancellations / failed payments later (we’ll add next)
    return {"received": True}
