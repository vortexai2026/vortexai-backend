# app/services/priority_engine.py

from datetime import datetime, date, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.seller_call import SellerCall
from app.models.followup import FollowUp

STATUS_POINTS = {
    "GREEN": 40,
    "CONTACTED": 20,
    "FOLLOW_UP": 30,
    "OFFER_SENT": 35,
    "UNDER_CONTRACT": 10,
    "ASSIGNED": 0,
    "DEAD": -999,
    "NEW": 5,
}

def _days_ago(dt):
    if not dt:
        return None
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).days

async def compute_priority_for_deal(db: AsyncSession, deal: Deal) -> tuple[float, str]:
    score = 0.0
    reasons = []

    # 1) Status
    status = (deal.status or "NEW").upper()
    score += STATUS_POINTS.get(status, 0)
    reasons.append(f"status={status}")

    if status == "DEAD":
        return -999.0, "DEAD"

    # 2) Motivation (latest seller call)
    call_q = (
        select(SellerCall)
        .where(SellerCall.deal_id == deal.id)
        .order_by(SellerCall.call_date.desc())
        .limit(1)
    )
    call_res = await db.execute(call_q)
    last_call = call_res.scalar_one_or_none()

    if last_call and last_call.motivation_level is not None:
        # motivation 1–5 => points 0..50
        mot = int(last_call.motivation_level)
        mot_points = max(0, min(5, mot)) * 10
        score += mot_points
        reasons.append(f"motivation={mot} (+{mot_points})")

    # 3) Follow-up due (overdue boosts strongly)
    today = date.today()
    fu_q = (
        select(func.count())
        .select_from(FollowUp)
        .where(
            FollowUp.deal_id == deal.id,
            FollowUp.completed == False,
            FollowUp.due_date <= today
        )
    )
    due_count = await db.scalar(fu_q)
    if due_count and due_count > 0:
        # due today or overdue
        boost = 25 + (min(5, due_count) * 5)
        score += boost
        reasons.append(f"followup_due={due_count} (+{boost})")

    # 4) Recency penalty (if not contacted recently, boost priority)
    days = _days_ago(getattr(deal, "last_contacted_at", None))
    if days is None:
        score += 10
        reasons.append("never_contacted (+10)")
    else:
        if days >= 7:
            score += 15
            reasons.append(f"last_contacted={days}d (+15)")
        elif days >= 3:
            score += 8
            reasons.append(f"last_contacted={days}d (+8)")

    # 5) If offer already sent, keep it hot
    if status == "OFFER_SENT":
        score += 10
        reasons.append("offer_hot (+10)")

    reason_text = "; ".join(reasons)
    return float(round(score, 2)), reason_text


async def refresh_priorities(db: AsyncSession, limit: int = 200) -> dict:
    """
    Updates priority_score + priority_reason on active deals.
    """
    q = (
        select(Deal)
        .where(Deal.status.in_(["NEW", "GREEN", "CONTACTED", "FOLLOW_UP", "OFFER_SENT", "UNDER_CONTRACT"]))
        .order_by(Deal.id.desc())
        .limit(limit)
    )
    res = await db.execute(q)
    deals = res.scalars().all()

    updated = 0
    for d in deals:
        p, reason = await compute_priority_for_deal(db, d)
        d.priority_score = p
        d.priority_reason = reason
        updated += 1

    await db.commit()

    return {"updated": updated, "limit": limit}
