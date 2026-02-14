from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.services.lifecycle_engine import apply_transition

router = APIRouter(tags=["Lifecycle"])


@router.post("/deals/{deal_id}/status/{new_status}")
async def update_deal_status(
    deal_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        return {"error": "Deal not found"}

    apply_transition(deal, new_status)

    await db.commit()

    return {
        "deal_id": deal.id,
        "new_status": deal.status
    }
