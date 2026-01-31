import os
import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/stripe", tags=["stripe"])

class CheckoutRequest(BaseModel):
    email: EmailStr

@router.post("/checkout")
def checkout(data: CheckoutRequest):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=data.email,
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "VortexAI Deal Access"},
                "unit_amount": 4900,
            },
            "quantity": 1
        }],
        success_url="https://vortexai.com/success",
        cancel_url="https://vortexai.com/cancel"
    )

    return {"checkout_url": session.url}
