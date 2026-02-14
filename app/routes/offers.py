from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
from app.models.deal import Deal
from app.services.offer_engine import calculate_mao

router = APIRouter()

@router.post("/deals/{deal_id}/send_offer")
async def send_offer(
    deal_id: int,
    arv: float,
    repairs: float,
    assignment_fee: float = 15000,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    mao = calculate_mao(arv, repairs, assignment_fee)

    deal.mao = mao
    deal.offer_sent_price = mao
    deal.offer_sent_at = datetime.utcnow()
    deal.offer_status = "SENT"
    deal.status = "OFFER_SENT"

    await db.commit()
    await db.refresh(deal)

    return {
        "message": "Offer sent",
        "mao": mao
    }
