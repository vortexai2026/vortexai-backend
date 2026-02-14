from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import AsyncSessionLocal
from app.models.deal import Deal
from app.models.buyer import Buyer
from app.models.buyer_interest import BuyerInterest

router = APIRouter()


class InterestRequest(BaseModel):
    buyer_email: str
    action: str = "interested"  # "interested" or "not_interested"


@router.post("/deals/{deal_id}/interest")
async def mark_interest(deal_id: int, body: InterestRequest):
    action = body.action.strip().lower()
    if action not in ("interested", "not_interested"):
        raise HTTPException(status_code=400, detail="action must be interested or not_interested")

    async with AsyncSessionLocal() as db:
        deal = await db.get(Deal, deal_id)
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")

        buyer = await db.scalar(select(Buyer).where(Buyer.email == body.buyer_email))
        if not buyer:
            raise HTTPException(status_code=404, detail="Buyer not found")

        existing = await db.scalar(
            select(BuyerInterest).where(
                BuyerInterest.deal_id == deal_id,
                BuyerInterest.buyer_id == buyer.id,
            )
        )

        if existing:
            existing.status = action
        else:
            db.add(BuyerInterest(buyer_id=buyer.id, deal_id=deal_id, status=action))

        # optional: move deal forward if interested
        if action == "interested" and deal.status in ("matched", "ai_processed", "new"):
            deal.status = "contacted"

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            # if unique constraint raced
            raise HTTPException(status_code=409, detail="Interest already exists")

        return {"ok": True, "deal_id": deal_id, "buyer_email": buyer.email, "status": action, "deal_status": deal.status}
