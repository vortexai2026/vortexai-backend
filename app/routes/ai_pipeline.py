from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models import Deal, Buyer  # adjust only if your models are elsewhere


router = APIRouter(prefix="/deals", tags=["AI Pipeline"])


def score_deal_basic(deal: Deal) -> dict:
    price = float(getattr(deal, "price", 0) or 0)
    arv = float(getattr(deal, "arv", 0) or 0)
    repairs = float(getattr(deal, "repairs", 0) or 0)

    profit = max(arv - price - repairs, 0)

    profit_score = min(100.0, (profit / 50000.0) * 100.0) if profit > 0 else 0.0
    urgency_score = 50.0
    risk_score = 30.0

    ai_score = (profit_score * 0.6) + (urgency_score * 0.25) + ((100 - risk_score) * 0.15)
    confidence = 0.70

    decision = "ignore"
    if ai_score >= 60:
        decision = "match_buyer"
    if ai_score >= 75:
        decision = "contact_seller"

    return {
        "profit_score": round(profit_score, 2),
        "urgency_score": round(urgency_score, 2),
        "risk_score": round(risk_score, 2),
        "ai_score": round(ai_score, 2),
        "ai_confidence": round(confidence, 2),
        "ai_decision": decision,
    }


@router.post("/{deal_id}/ai_process")
async def ai_process_deal(deal_id: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    if getattr(deal, "ai_processed_at", None):
        return {"ok": True, "message": "Already processed"}

    scores = score_deal_basic(deal)

    # Try match buyer (simple example: first buyer in DB)
    matched_buyer_id = None
    if scores["ai_decision"] in ("match_buyer", "contact_seller"):
        buyer_result = await db.execute(select(Buyer))
        buyer = buyer_result.scalars().first()
        if buyer:
            matched_buyer_id = buyer.id

    # Update deal
    for key, value in scores.items():
        if hasattr(deal, key):
            setattr(deal, key, value)

    if hasattr(deal, "matched_buyer_id"):
        deal.matched_buyer_id = matched_buyer_id

    if hasattr(deal, "status"):
        deal.status = "ai_processed"

    if hasattr(deal, "ai_processed_at"):
        deal.ai_processed_at = datetime.now(timezone.utc)

    await db.commit()

    return {
        "ok": True,
        "deal_id": deal_id,
        "matched_buyer_id": matched_buyer_id,
        "scores": scores,
        "status": getattr(deal, "status", None),
    }
