import os
import stripe
import psycopg2
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")
if not STRIPE_SECRET_KEY:
    raise RuntimeError("STRIPE_SECRET_KEY not set")
if not STRIPE_WEBHOOK_SECRET:
    raise RuntimeError("STRIPE_WEBHOOK_SECRET not set (Stripe webhook secret)")

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/stripe", tags=["stripe"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def set_buyer_paid(email: str, customer_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE buyers
            SET tier='paid',
                plan='pro',
                stripe_customer_id=%s
            WHERE email=%s
        """, (customer_id, email))
        conn.commit()
        cur.close()
    finally:
        conn.close()

def set_buyer_free(email: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE buyers
            SET tier='free',
                plan='free'
            WHERE email=%s
        """, (email,))
        conn.commit()
        cur.close()
    finally:
        conn.close()

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    event_type = event.get("type")

    # ✅ When checkout completes, buyer becomes PAID
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        customer_details = session.get("customer_details") or {}
        email = (customer_details.get("email") or "").strip().lower()

        if email and customer_id:
            set_buyer_paid(email, customer_id)

    # ✅ If subscription is canceled or unpaid later, downgrade to FREE
    # This helps you keep access strict.
    if event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        sub = event["data"]["object"]
        customer_id = sub.get("customer")

        # lookup customer email
        try:
            customer = stripe.Customer.retrieve(customer_id)
            email = (customer.get("email") or "").strip().lower()
        except Exception:
            email = ""

        status = sub.get("status")  # active, trialing, past_due, canceled, unpaid, etc.

        # downgrade if canceled/unpaid
        if email and status in ("canceled", "unpaid"):
            set_buyer_free(email)

        # upgrade/ensure paid if active
        if email and status in ("active", "trialing"):
            set_buyer_paid(email, customer_id)

    return {"status": "ok"}
