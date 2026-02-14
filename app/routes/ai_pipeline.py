from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.monetization import ensure_monthly_reset, can_receive_match, consume_match

router = APIRouter(tags=["AI Pipeline"])


@router.post("/deals/{deal_id}/ai_process")
async def ai_process_deal(deal_id: int, db: AsyncSession = Depends(get_db)):

    # Load deal
    res = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = res.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Basic scoring (you can swap later)
    price = float(deal.price or 0)
    score = max(0.0, 100.0 - (price / 1000.0))
    deal.score = round(score, 2)

    # Decide
    decision = "ignore"
    if deal.score >= 60:
        decision = "match_buyer"
    if deal.score >= 75:
        decision = "contact_seller"
    deal.ai_decision = decision

    # If not worth processing, mark and return
    if decision == "ignore":
        deal.status = "ai_processed"
        deal.ai_processed_at = datetime.now(timezone.utc)
        await db.commit()
        return {"ok": True, "deal_id": deal.id, "decision": decision, "score": deal.score}

    # Find active buyers
    buyers_res = await db.execute(select(Buyer).where(Buyer.is_active == True))
    buyers = buyers_res.scalars().all()

    # Filter buyers by preference + budget
    eligible = []
    for b in buyers:
        ensure_monthly_reset(b)
        if (
            (b.asset_type == deal.asset_type)
            and (b.city == deal.city)
            and (float(b.max_budget or 0) >= float(deal.price or 0))
        ):
            ok, _msg = can_receive_match(b)
            if ok:
                eligible.append(b)

    # No eligible buyer
    if not eligible:
        deal.status = "ai_processed"
        deal.ai_processed_at = datetime.now(timezone.utc)
        deal.matched_buyer_id = None
        await db.commit()
        return {
            "ok": True,
            "deal_id": deal.id,
            "decision": decision,
            "score": deal.score,
            "matched_buyer_id": None,
            "note": "No eligible buyers (or tier limits blocked them)."
        }

    # Pick best buyer (simple: highest budget)
    best = sorted(eligible, key=lambda x: float(x.max_budget or 0), reverse=True)[0]

    # Consume match (monetization enforcement)
    consume_match(best)

    # Update deal lifecycle
    deal.matched_buyer_id = best.id
    deal.status = "matched"
    deal.ai_processed_at = datetime.now(timezone.utc)

    await db.commit()

    return {
        "ok": True,
        "deal_id": deal.id,
        "decision": decision,
        "score": deal.score,
        "matched_buyer_id": best.id,
        "buyer_tier": best.tier,
        "buyer_monthly_match_count": best.monthly_match_count,
    }
