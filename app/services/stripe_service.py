import os
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

TIER_TO_PRICE_ENV = {
    "free49": "STRIPE_PRICE_FREE_49",
    "pro199": "STRIPE_PRICE_PRO_199",
    "elite499": "STRIPE_PRICE_ELITE_499",
}

def get_price_id_for_tier(tier: str) -> str:
    env_key = TIER_TO_PRICE_ENV.get(tier)
    if not env_key:
        raise ValueError("Invalid tier")
    price_id = os.getenv(env_key)
    if not price_id:
        raise RuntimeError(f"Missing env var: {env_key}")
    return price_id

def create_checkout_session(*, buyer_email: str, tier: str, success_url: str, cancel_url: str, buyer_id: int):
    price_id = get_price_id_for_tier(tier)

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=buyer_email,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "buyer_id": str(buyer_id),
            "tier": tier,
        },
    )
    return session
