import os
import stripe
from fastapi import APIRouter, Request, HTTPException
from app.database import execute

router = APIRouter(prefix="/stripe", tags=["stripe"])

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/webhook")
async def webhook(request: Request):
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured")

    stripe.api_key = STRIPE_SECRET_KEY

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    # Example: subscription paid → upgrade buyer
    if event["type"] in ("checkout.session.completed", "invoice.paid"):
        obj = event["data"]["object"]
        buyer_email = (obj.get("customer_email") or obj.get("metadata", {}).get("buyer_email") or "").lower().strip()
        if buyer_email:
            execute("UPDATE buyers SET plan='pro', tier='paid' WHERE email=%s", (buyer_email,))

    return {"status": "ok"}
