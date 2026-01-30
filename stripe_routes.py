import os
import stripe
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/stripe", tags=["stripe"])

@router.post("/checkout")
def create_checkout():
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{
            "price": "price_BUYER_PRO",  # replace with your real Price ID
            "quantity": 1
        }],
        success_url=f"{os.getenv('APP_URL')}/success",
        cancel_url=f"{os.getenv('APP_URL')}/cancel"
    )
    return {"url": session.url}
