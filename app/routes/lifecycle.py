from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models.deal import Deal

router = APIRouter(tags=["Lifecycle"])


ALLOWED_TRANSITIONS = {
    "new": ["ai_processed", "dead"],
    "ai_processed": ["matched", "dead"],
    "matched": ["contacted", "dead"],
    "contacted": ["under_contract", "dead"],
    "under_contract": ["closed", "dead"],
    "closed": [],
    "dead": []
}


@router.post("/deals/{deal_id}/transition/{new_status}")
async def transition_deal(
    deal_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    current_status = deal.status or "new"

    if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from '{current_status}' to '{new_status}'"
        )

    deal.status = new_status
    deal.updated_at = datetime.now(timezone.utc)

    # If deal closes → calculate actual profit automatically
    if new_status == "closed" and deal.assignment_fee:
        deal.actual_profit = deal.assignment_fee

    await db.commit()

    return {
        "ok": True,
        "deal_id": deal.id,
        "old_status": current_status,
        "new_status": new_status
    }
