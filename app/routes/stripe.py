# app/routes/stripe.py
from fastapi import APIRouter
router = APIRouter(tags=["Stripe"])

@router.post("/stripe/checkout")
async def checkout(amount: float):
    return {"ok": True, "checkout_url": f"https://checkout.stripe.com/pay/{amount}"}
