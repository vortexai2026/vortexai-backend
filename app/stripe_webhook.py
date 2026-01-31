import os
import stripe
import psycopg2
from fastapi import APIRouter, Request, HTTPException

DATABASE_URL = os.getenv("DATABASE_URL")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/stripe", tags=["stripe"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@router.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["customer_email"]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE buyers SET tier='paid', plan='pro' WHERE email=%s",
            (email,)
        )
        conn.commit()
        cur.close()
        conn.close()

    return {"status": "ok"}
