import os
import uuid
import stripe
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.database import fetch_one, execute
from app.models import CheckoutRequest

router = APIRouter(prefix="/stripe", tags=["stripe"])

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")

def stripe_ready():
    return bool(STRIPE_SECRET_KEY and STRIPE_PRICE_ID)

@router.post("/checkout")
def checkout(payload: CheckoutRequest):
    if not stripe_ready():
        raise HTTPException(status_code=503, detail="Stripe not configured (set STRIPE_SECRET_KEY + STRIPE_PRICE_ID)")

    stripe.api_key = STRIPE_SECRET_KEY

    email = payload.email.strip().lower()

    buyer = fetch_one("SELECT id FROM buyers WHERE email=%s LIMIT 1", (email,))
    if not buyer:
        buyer_id = str(uuid.uuid4())
        execute("""
            INSERT INTO buyers (id, email, name, location, asset_type, budget, tier, plan)
            VALUES (%s,%s,%s,%s,%s,%s,'free','free')
        """, (buyer_id, email, payload.name, payload.location, payload.asset_type, payload.budget))
    else:
        buyer_id = str(buyer["id"])

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            customer_email=email,
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
            success_url=f"{APP_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{APP_URL}/cancel",
            metadata={"buyer_email": email, "buyer_id": buyer_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"checkout_url": session.url, "buyer_id": buyer_id})
