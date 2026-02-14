from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.deal import Deal

router = APIRouter()


ALLOWED = {"new", "ai_processed", "matched", "contacted", "under_contract", "closed", "dead"}


class StatusUpdate(BaseModel):
    status: str
    actual_profit: float | None = None


@router.post("/deals/{deal_id}/status")
async def update_deal_status(deal_id: int, body: StatusUpdate):
    status = body.status.strip().lower()
    if status not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(ALLOWED)}")

    async with AsyncSessionLocal() as db:
        deal = await db.get(Deal, deal_id)
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")

        deal.status = status

        # if closing, store profit (optional)
        if status == "closed" and body.actual_profit is not None:
            deal.actual_profit = float(body.actual_profit)

        await db.commit()
        return {"ok": True, "deal_id": deal_id, "status": deal.status, "actual_profit": deal.actual_profit}
