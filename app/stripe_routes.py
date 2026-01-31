import os
import uuid
import stripe
import psycopg2
from fastapi import APIRouter
from fastapi.responses import JSONResponse

DATABASE_URL = os.getenv("DATABASE_URL")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/stripe", tags=["stripe"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@router.post("/checkout")
def checkout(payload: dict):
    email = payload.get("email")
    if not email:
        return JSONResponse(status_code=400, content={"error": "email required"})

    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        customer_email=email,
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        success_url=f"{APP_URL}/success",
        cancel_url=f"{APP_URL}/cancel",
    )

    return {"checkout_url": session.url}
