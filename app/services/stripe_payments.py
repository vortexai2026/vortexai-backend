import os
import stripe

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:8000").strip()

def init_stripe():
    if not STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY missing")
    stripe.api_key = STRIPE_SECRET_KEY

def create_assignment_checkout(deal_id: int, amount_usd: float) -> str:
    """
    Creates Stripe Checkout link for assignment fee collection.
    """
    init_stripe()

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Assignment Fee - Deal #{deal_id}"},
                "unit_amount": int(amount_usd * 100),
            },
            "quantity": 1
        }],
        success_url=f"{FRONTEND_BASE_URL}/success?deal_id={deal_id}",
        cancel_url=f"{FRONTEND_BASE_URL}/cancel?deal_id={deal_id}",
        metadata={"deal_id": str(deal_id), "type": "assignment_fee"},
    )
    return session.url
