import os
import json
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import stripe

from app.database import get_db
from app.models.buyer import Buyer

router = APIRouter(tags=["Stripe Webhook"])

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Price IDs (already in your Railway variables)
PRICE_VIP = os.getenv("STRIPE_PRICE_VIP", "")
PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")
PRICE_ELITE = os.getenv("STRIPE_PRICE_ELITE", "")

stripe.api_key = STRIPE_SECRET_KEY


def tier_from_price_id(price_id: str) -> str:
    if price_id == PRICE_ELITE:
        return "elite"
    if price_id == PRICE_PRO:
        return "pro"
    if price_id == PRICE_VIP:
        return "vip"
    return "free"


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = next(get_db())):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET missing")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    # We handle completed checkout sessions
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        buyer_email = session.get("customer_details", {}).get("email")
        if not buyer_email:
            return {"ok": True, "note": "No email in checkout session"}

        # fetch line items to see what was purchased
        line_items = stripe.checkout.Session.list_line_items(session["id"], limit=5)
        if not line_items or not line_items["data"]:
            return {"ok": True, "note": "No line items found"}

        price_id = line_items["data"][0]["price"]["id"]
        new_tier = tier_from_price_id(price_id)

        # find buyer by email
        res = await db.execute(select(Buyer).where(Buyer.email == buyer_email))
        buyer = res.scalar_one_or_none()

        if not buyer:
            return {"ok": True, "note": f"No buyer found for email {buyer_email}"}

        buyer.tier = new_tier
        buyer.is_active = True

        await db.commit()

        return {"ok": True, "buyer_email": buyer_email, "tier": new_tier}

    return {"ok": True, "ignored_event": event["type"]}
