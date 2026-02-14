import os
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_assignment_checkout_session(
    deal_id: int,
    buyer_id: int,
    buyer_email: str,
    amount_usd: float,
    success_url: str,
    cancel_url: str
):
    """
    Creates a Stripe Checkout Session for assignment fee / deposit.
    amount_usd is in dollars, Stripe needs cents.
    """
    if not stripe.api_key:
        raise RuntimeError("STRIPE_SECRET_KEY is missing")

    amount_cents = int(round(float(amount_usd) * 100))

    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=buyer_email,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Assignment Fee / Deposit (Deal #{deal_id})"
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }
        ],
        metadata={
            "deal_id": str(deal_id),
            "buyer_id": str(buyer_id),
            "purpose": "assignment_fee"
        },
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return session
