from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer

router = APIRouter(tags=["AI Pipeline"])


@router.post("/deals/{deal_id}/ai_process")
async def ai_process_deal(deal_id: int, db: AsyncSession = Depends(get_db)):

    # Get deal
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Simple AI scoring logic (based only on price)
    price = float(deal.price or 0)

    # Example logic:
    # cheaper deals = higher score
    score = max(0, 100 - (price / 1000))

    # Match buyers
    matched_buyers = []

    buyer_result = await db.execute(select(Buyer).where(Buyer.is_active == True))
    buyers = buyer_result.scalars().all()

    for buyer in buyers:
        if (
            buyer.asset_type == deal.asset_type
            and buyer.city == deal.city
            and buyer.max_budget >= deal.price
        ):
            matched_buyers.append({
                "buyer_id": buyer.id,
                "buyer_name": buyer.name,
                "buyer_email": buyer.email
            })

    # Update deal score field (this exists in your model)
    deal.score = round(score, 2)

    await db.commit()

    return {
        "ok": True,
        "deal_id": deal.id,
        "new_score": deal.score,
        "matched_buyers": matched_buyers
    }
