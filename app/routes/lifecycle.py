from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.deal import Deal

router = APIRouter()

ALLOWED_STATUSES = {
    "NEW",
    "GREEN",
    "CONTACTED",
    "FOLLOW_UP",
    "OFFER_SENT",
    "UNDER_CONTRACT",
    "ASSIGNED",
    "DEAD"
}

@router.post("/deals/{deal_id}/status/{new_status}")
async def update_status(
    deal_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db)
):

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal.status = new_status
    await db.commit()
    await db.refresh(deal)

    return {"message": "Status updated", "status": deal.status}
