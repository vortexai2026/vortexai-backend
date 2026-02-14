from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.monetization import ensure_monthly_reset, can_receive_match, consume_match


async def process_deal(db: AsyncSession, deal: Deal) -> dict:
    """
    Processes one deal:
    - score deal
    - decide action
    - enforce tier limits
    - match buyer
    - update lifecycle fields
    """

    # --- score ---
    price = float(deal.price or 0)
    score = max(0.0, 100.0 - (price / 1000.0))
    deal.score = round(score, 2)

    # --- decision ---
    decision = "ignore"
    if deal.score >= 60:
        decision = "match_buyer"
    if deal.score >= 75:
        decision = "contact_seller"

    deal.ai_decision = decision
    deal.ai_processed_at = datetime.now(timezone.utc)

    # Ignore path
    if decision == "ignore":
        deal.status = "ai_processed"
        deal.matched_buyer_id = None
        return {
            "deal_id": deal.id,
            "decision": decision,
            "score": deal.score,
            "matched_buyer_id": None,
            "status": deal.status,
        }

    # --- get buyers ---
    buyers_res = await db.execute(select(Buyer).where(Buyer.is_active == True))
    buyers = buyers_res.scalars().all()

    eligible = []
    blocked = []

    for b in buyers:
        ensure_monthly_reset(b)

        # preference filter
        if b.asset_type != deal.asset_type:
            continue
        if b.city != deal.city:
            continue
        if float(b.max_budget or 0) < float(deal.price or 0):
            continue

        ok, msg = can_receive_match(b)
        if ok:
            eligible.append(b)
        else:
            blocked.append({"buyer_id": b.id, "tier": b.tier, "reason": msg})

    if not eligible:
        deal.status = "ai_processed"
        deal.matched_buyer_id = None
        return {
            "deal_id": deal.id,
            "decision": decision,
            "score": deal.score,
            "matched_buyer_id": None,
            "status": deal.status,
            "blocked": blocked,
        }

    # pick best buyer (highest budget)
    best = sorted(eligible, key=lambda x: float(x.max_budget or 0), reverse=True)[0]

    # consume match (monetization enforcement)
    consume_match(best)

    # lifecycle
    deal.matched_buyer_id = best.id
    deal.status = "matched"

    return {
        "deal_id": deal.id,
        "decision": decision,
        "score": deal.score,
        "matched_buyer_id": best.id,
        "status": deal.status,
        "buyer_tier": best.tier,
        "buyer_monthly_match_count": best.monthly_match_count,
    }
