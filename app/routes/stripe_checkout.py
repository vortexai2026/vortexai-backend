from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()


class CheckoutRequest(BaseModel):
    email: str
    tier: str  # "pro" or "elite"


# Replace these with your real Stripe Price IDs
PRICE_MAP = {
    "pro": "price_pro_id_here",
    "elite": "price_elite_id_here",
}


@router.post("/stripe/checkout")
async def create_checkout_session(data: CheckoutRequest):

    if data.tier not in PRICE_MAP:
        raise HTTPException(status_code=400, detail="Invalid tier")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=data.email,
            line_items=[
                {
                    "price": PRICE_MAP[data.tier],
                    "quantity": 1,
                }
            ],
            success_url="https://yourdomain.com/success",
            cancel_url="https://yourdomain.com/cancel",
        )

        return {"checkout_url": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
