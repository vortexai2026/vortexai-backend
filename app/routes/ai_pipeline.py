from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models.deal import Deal

router = APIRouter(tags=["AI Pipeline"])


@router.post("/deals/{deal_id}/ai_process")
async def ai_process_deal(deal_id: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    price = float(getattr(deal, "price", 0) or 0)
    arv = float(getattr(deal, "arv", 0) or 0)
    repairs = float(getattr(deal, "repairs", 0) or 0)

    profit = max(arv - price - repairs, 0)

    profit_score = min(100.0, (profit / 50000.0) * 100.0) if profit > 0 else 0.0
    urgency_score = 50.0
    risk_score = 30.0

    ai_score = (profit_score * 0.6) + (urgency_score * 0.25) + ((100 - risk_score) * 0.15)

    decision = "ignore"
    if ai_score >= 60:
        decision = "review"
    if ai_score >= 75:
        decision = "high_priority"

    if hasattr(deal, "profit_score"):
        deal.profit_score = round(profit_score, 2)

    if hasattr(deal, "ai_score"):
        deal.ai_score = round(ai_score, 2)

    if hasattr(deal, "ai_decision"):
        deal.ai_decision = decision

    if hasattr(deal, "status"):
        deal.status = "ai_processed"

    if hasattr(deal, "ai_processed_at"):
        deal.ai_processed_at = datetime.now(timezone.utc)

    await db.commit()

    return {
        "ok": True,
        "deal_id": deal_id,
        "profit_score": profit_score,
        "ai_score": ai_score,
        "decision": decision,
    }
