from fastapi import APIRouter, Request, HTTPException
import stripe
import os

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.buyer import Buyer

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    # Handle subscription success
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]
        email = session.get("customer_email")

        # Example: map price ID to tier
        line_items = stripe.checkout.Session.list_line_items(session["id"])
        price_id = line_items["data"][0]["price"]["id"]

        tier_map = {
            "price_pro_id": "pro",
            "price_elite_id": "elite",
        }

        tier = tier_map.get(price_id)

        if tier and email:
            async with AsyncSessionLocal() as db:
                buyer = await db.scalar(
                    select(Buyer).where(Buyer.email == email)
                )
                if buyer:
                    buyer.tier = tier
                    buyer.is_active = True
                    await db.commit()

    return {"status": "success"}
