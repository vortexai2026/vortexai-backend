import os
import stripe
import psycopg2
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/stripe", tags=["stripe"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ✅ Payment completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        customer_email = session["customer_details"]["email"]
        customer_id = session["customer"]

        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE buyers
                SET tier = 'paid',
                    plan = 'pro',
                    stripe_customer_id = %s
                WHERE email = %s
            """, (customer_id, customer_email))
            conn.commit()
            cur.close()
        finally:
            conn.close()

    return {"status": "ok"}
