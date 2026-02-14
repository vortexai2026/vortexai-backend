from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer

router = APIRouter()


# -------------------------------
# LIST DEALS
# -------------------------------
@router.get("/deals/", tags=["Deals"])
async def list_deals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal))
    return result.scalars().all()


# -------------------------------
# CREATE DEAL
# -------------------------------
@router.post("/deals/create", tags=["Deals"])
async def create_deal(deal_data: dict, db: AsyncSession = Depends(get_db)):
    new_deal = Deal(**deal_data)
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)
    return new_deal


# -------------------------------
# AI PROCESS DEAL
# -------------------------------
@router.post("/deals/{deal_id}/ai_process", tags=["AI Pipeline"])
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
        decision = "match_buyer"
    if ai_score >= 75:
        decision = "contact_seller"

    matched_buyer_id = None
    if decision in ("match_buyer", "contact_seller"):
        buyer_result = await db.execute(select(Buyer))
        buyer = buyer_result.scalars().first()
        if buyer:
            matched_buyer_id = buyer.id

    if hasattr(deal, "profit_score"):
        deal.profit_score = round(profit_score, 2)

    if hasattr(deal, "ai_score"):
        deal.ai_score = round(ai_score, 2)

    if hasattr(deal, "ai_decision"):
        deal.ai_decision = decision

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
        "profit_score": profit_score,
        "ai_score": ai_score,
        "decision": decision,
        "matched_buyer_id": matched_buyer_id,
    }
