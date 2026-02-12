from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["stripe"])

class CheckoutRequest(BaseModel):
    amount: float
    currency: str = "USD"

@router.post("/stripe/checkout")
def stripe_checkout(request: CheckoutRequest):
    return {"status": "success", "amount": request.amount, "currency": request.currency}
