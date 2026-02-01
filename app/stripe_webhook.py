import os
import stripe
from fastapi import APIRouter, Request, HTTPException
from app.database import execute

router = APIRouter(prefix="/stripe", tags=["stripe"])

@router.post("/webhook")
async def webhook(request: Request):
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    stripe_key = os.getenv("STRIPE_SECRET_KEY")

    if not endpoint_secret or not stripe_key:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured.")

    stripe.api_key = stripe_key

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    # Example: subscription activated
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        buyer_id = session.get("metadata", {}).get("buyer_id")
        if buyer_id:
            execute("UPDATE buyers SET tier='paid', plan='pro' WHERE id=%s", (buyer_id,))

    return {"received": True}
