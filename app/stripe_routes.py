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
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")

# -----------------------------------------------------
# SAFETY CHECKS (DO NOT CRASH APP)
# -----------------------------------------------------
STRIPE_ENABLED = True

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
    STRIPE_ENABLED = False
    print("⚠️ Stripe disabled (missing STRIPE_SECRET_KEY or STRIPE_PRICE_ID)")

if STRIPE_ENABLED:
    stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/stripe", tags=["stripe"])

# -----------------------------------------------------
# DB
# -----------------------------------------------------
def get_conn():
    return psycopg2.connect(DATABASE_URL)

# -----------------------------------------------------
# STRIPE CHECKOUT
# -----------------------------------------------------
@router.post("/checkout")
def create_checkout(payload: dict):
    """
    Creates a Stripe checkout session for a buyer subscription.
    SAFE MODE: returns clear message if Stripe is disabled.
    """

    if not STRIPE_ENABLED:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Stripe is not configured yet",
                "message": "Payments are temporarily disabled. Please try again later."
            }
        )

    email = (payload.get("email") or "").strip().lower()
    if not email:
        return JSONResponse(status_code=400, content={"error": "email is required"})

    name = payload.get("name")
    location = payload.get("location")
    asset_type = payload.get("asset_type")
    budget = payload.get("budget")

    # -------------------------------------------------
    # Create / update buyer as FREE
    # Webhook upgrades to PAID
    # -------------------------------------------------
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
                INSERT INTO buyers
                (id, name, email, budget, location, asset_type, plan, tier)
                VALUES (%s,%s,%s,%s,%s,%s,'free','free')
            """, (buyer_id, name, email, budget, location, asset_type))

        conn.commit()
        cur.close()
    finally:
        conn.close()

    # -------------------------------------------------
    # Create Stripe Checkout Session
    # -------------------------------------------------
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

    return {
        "status": "ok",
        "checkout_url": session.url,
        "buyer_id": buyer_id
    }
