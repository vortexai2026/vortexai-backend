from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models import Deal, Buyer  # adjust if your model names differ
from app.matching import find_best_buyer_for_deal  # adjust if your function name differs

router = APIRouter(prefix="/deals", tags=["Deals"])

def score_deal_basic(deal: Deal) -> dict:
    """
    Simple scoring logic to prove the pipeline.
    You can later swap this to your AI modules (ai_level2_scoring, ai_decision, etc.)
    """
    # Safe defaults
    price = float(getattr(deal, "price", 0) or 0)
    arv = float(getattr(deal, "arv", 0) or 0)
    repairs = float(getattr(deal, "repairs", 0) or 0)

    # Profit: (ARV - price - repairs)
    profit = max(arv - price - repairs, 0)

    # Normalize to scores 0-100 (basic)
    profit_score = min(100.0, (profit / 50000.0) * 100.0) if profit > 0 else 0.0
    urgency_score = 50.0  # placeholder until you add rules
    risk_score = 30.0     # placeholder until you add rules

    ai_score = (profit_score * 0.6) + (urgency_score * 0.25) + ((100 - risk_score) * 0.15)
    confidence = 0.65  # placeholder confidence

    # Decision
    decision = "ignore"
    if ai_score >= 60:
        decision = "match_buyer"
    if ai_score >= 75:
        decision = "contact_seller"

    return {
        "profit_score": float(round(profit_score, 2)),
        "urgency_score": float(round(urgency_score, 2)),
        "risk_score": float(round(risk_score, 2)),
        "ai_score": float(round(ai_score, 2)),
        "ai_confidence": float(round(confidence, 2)),
        "ai_decision": decision,
    }

@router.post("/{deal_id}/ai_process")
async def ai_process_deal(deal_id: str, db: AsyncSession = Depends(get_db)):
    # Load deal
    res = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = res.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Prevent double-processing (optional)
    if getattr(deal, "ai_processed_at", None):
        return {"ok": True, "message": "Deal already AI processed", "deal_id": deal_id}

    # Score + decide
    scores = score_deal_basic(deal)

    # Match buyer if decision says so
    matched_buyer_id = None
    if scores["ai_decision"] in ("match_buyer", "contact_seller"):
        try:
            matched_buyer_id = await find_best_buyer_for_deal(db, deal)  # should return buyer_id or None
        except Exception:
            matched_buyer_id = None

    # Update deal fields (only if your Deal model contains these columns)
    for k, v in scores.items():
        if hasattr(deal, k):
            setattr(deal, k, v)

    if hasattr(deal, "matched_buyer_id"):
        setattr(deal, "matched_buyer_id", matched_buyer_id)

    if hasattr(deal, "status"):
        setattr(deal, "status", "ai_processed")

    if hasattr(deal, "ai_processed_at"):
        setattr(deal, "ai_processed_at", datetime.now(timezone.utc))

    await db.commit()

    return {
        "ok": True,
        "deal_id": deal_id,
        "matched_buyer_id": matched_buyer_id,
        "scores": scores,
        "status": getattr(deal, "status", None),
    }
