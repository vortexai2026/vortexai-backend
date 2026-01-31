import os
import stripe
from fastapi import APIRouter, Request, HTTPException
from app.database import execute

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY:
    raise RuntimeError("STRIPE_SECRET_KEY not set")
if not STRIPE_WEBHOOK_SECRET:
    raise RuntimeError("STRIPE_WEBHOOK_SECRET not set")

stripe.api_key = STRIPE_SECRET_KEY
router = APIRouter(prefix="/stripe", tags=["stripe"])

def set_paid(email: str, customer_id: str):
    execute("""
        UPDATE buyers
        SET tier='paid', plan='pro', stripe_customer_id=%s
        WHERE email=%s
    """, (customer_id, email))

def set_free(email: str):
    execute("""
        UPDATE buyers
        SET tier='free', plan='free'
        WHERE email=%s
    """, (email,))

@router.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    t = event.get("type")

    if t == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        email = ((session.get("customer_details") or {}).get("email") or "").strip().lower()
        if email and customer_id:
            set_paid(email, customer_id)

    if t in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        status = sub.get("status")

        try:
            cust = stripe.Customer.retrieve(customer_id)
            email = (cust.get("email") or "").strip().lower()
        except Exception:
            email = ""

        if email and status in ("active", "trialing"):
            set_paid(email, customer_id)
        if email and status in ("canceled", "unpaid"):
            set_free(email)

    return {"status": "ok"}
