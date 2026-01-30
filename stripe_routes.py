import os
import uuid
import stripe
import psycopg2
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")

# REQUIRED: set in your .env / Railway variables
# STRIPE_PRICE_ID should be your Stripe recurring price id for $99/mo
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")
if not STRIPE_SECRET_KEY:
    raise RuntimeError("STRIPE_SECRET_KEY not set")
if not STRIPE_PRICE_ID:
    raise RuntimeError("STRIPE_PRICE_ID not set (create price in Stripe and paste here)")

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/stripe", tags=["stripe"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@router.post("/checkout")
def create_checkout(payload: dict):
    """
    Creates a Stripe checkout session for a buyer subscription.
    payload expects:
      - email (required)
      - name (optional)
      - location (optional)
      - asset_type (optional)
      - budget (optional)
    """
    email = (payload.get("email") or "").strip().lower()
    if not email:
        return JSONResponse(status_code=400, content={"error": "email is required"})

    name = payload.get("name")
    location = payload.get("location")
    asset_type = payload.get("asset_type")
    budget = payload.get("budget")

    # Create/update buyer as FREE first (webhook upgrades to PAID)
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM buyers WHERE email=%s LIMIT 1", (email,))
        row = cur.fetchone()

        if row:
            buyer_id = str(row[0])
            cur.execute("""
                UPDATE buyers
                SET name=COALESCE(%s,name),
                    location=COALESCE(%s,location),
                    asset_type=COALESCE(%s,asset_type),
                    budget=COALESCE(%s,budget),
                    tier=COALESCE(tier,'free'),
                    plan=COALESCE(plan,'free')
                WHERE email=%s
            """, (name, location, asset_type, budget, email))
        else:
            buyer_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO buyers (id, name, email, budget, location, asset_type, plan, tier)
                VALUES (%s,%s,%s,%s,%s,%s,'free','free')
            """, (buyer_id, name, email, budget, location, asset_type))

        conn.commit()
        cur.close()
    finally:
        conn.close()

    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        customer_email=email,
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        success_url=f"{APP_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{APP_URL}/cancel",
        metadata={
            "buyer_email": email,
            "buyer_id": buyer_id
        }
    )

    return {"checkout_url": session.url, "buyer_id": buyer_id}
