import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.stripe_checkout_engine import create_assignment_checkout_session

router = APIRouter()

@router.post("/deals/{deal_id}/collect_assignment/{buyer_id}")
async def collect_assignment_fee(
    deal_id: int,
    buyer_id: int,
    amount_usd: float = 15000,
    db: AsyncSession = Depends(get_db)
):
    # Load deal
    r1 = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = r1.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Load buyer
    r2 = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    buyer = r2.scalar_one_or_none()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    buyer_email = getattr(buyer, "email", None)
    if not buyer_email:
        raise HTTPException(status_code=400, detail="Buyer has no email")

    # URLs (set these in Railway env)
    success_url = os.getenv("STRIPE_SUCCESS_URL", "https://example.com/success")
    cancel_url = os.getenv("STRIPE_CANCEL_URL", "https://example.com/cancel")

    session = create_assignment_checkout_session(
        deal_id=deal_id,
        buyer_id=buyer_id,
        buyer_email=buyer_email,
        amount_usd=amount_usd,
        success_url=success_url,
        cancel_url=cancel_url
    )

    # Save to deal
    deal.assignment_fee = amount_usd
    deal.stripe_session_id = session.id
    deal.stripe_payment_status = "PENDING"

    await db.commit()
    await db.refresh(deal)

    return {
        "message": "Checkout session created",
        "deal_id": deal.id,
        "buyer_id": buyer.id,
        "amount_usd": amount_usd,
        "checkout_url": session.url,
        "stripe_session_id": session.id
    }
