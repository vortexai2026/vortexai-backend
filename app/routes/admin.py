from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import datetime, timezone

from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer

router = APIRouter(tags=["Admin"])


@router.get("/admin/metrics")
async def admin_metrics(db: AsyncSession = Depends(get_db)):
    # Totals
    total_deals = await db.scalar(select(func.count()).select_from(Deal))
    total_buyers = await db.scalar(select(func.count()).select_from(Buyer))

    # Deals by status
    status_rows = await db.execute(
        select(Deal.status, func.count()).group_by(Deal.status)
    )
    deals_by_status = {s or "unknown": c for s, c in status_rows.all()}

    # Buyers by tier
    tier_rows = await db.execute(
        select(Buyer.tier, func.count()).group_by(Buyer.tier)
    )
    buyers_by_tier = {t or "unknown": c for t, c in tier_rows.all()}

    # Matched / contacted / closed counts (conversion funnel)
    matched_count = await db.scalar(
        select(func.count()).select_from(Deal).where(Deal.matched_buyer_id.isnot(None))
    )
    contacted_count = await db.scalar(
        select(func.count()).select_from(Deal).where(Deal.status == "contacted")
    )
    under_contract_count = await db.scalar(
        select(func.count()).select_from(Deal).where(Deal.status == "under_contract")
    )
    closed_count = await db.scalar(
        select(func.count()).select_from(Deal).where(Deal.status == "closed")
    )

    # Profit totals
    total_expected_profit = await db.scalar(
        select(func.coalesce(func.sum(Deal.expected_profit), 0.0))
    )
    total_assignment_fee = await db.scalar(
        select(func.coalesce(func.sum(Deal.assignment_fee), 0.0))
    )
    total_actual_profit = await db.scalar(
        select(func.coalesce(func.sum(Deal.actual_profit), 0.0))
    )

    # Average score
    avg_score = await db.scalar(
        select(func.coalesce(func.avg(Deal.score), 0.0))
    )

    # Top cities by deal volume
    top_cities_rows = await db.execute(
        select(Deal.city, func.count())
        .group_by(Deal.city)
        .order_by(func.count().desc())
        .limit(10)
    )
    top_cities = [{"city": city, "deal_count": cnt} for city, cnt in top_cities_rows.all()]

    # Top buyers by matches
    top_buyers_rows = await db.execute(
        select(Buyer.id, Buyer.name, Buyer.email, Buyer.tier, Buyer.total_matches)
        .order_by(Buyer.total_matches.desc())
        .limit(10)
    )
    top_buyers = [
        {
            "buyer_id": bid,
            "name": name,
            "email": email,
            "tier": tier,
            "total_matches": matches,
        }
        for bid, name, email, tier, matches in top_buyers_rows.all()
    ]

    # This month metrics
    now = datetime.now(timezone.utc)
    start_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    deals_created_this_month = await db.scalar(
        select(func.count()).select_from(Deal).where(Deal.created_at >= start_month)
    )

    matched_this_month = await db.scalar(
        select(func.count())
        .select_from(Deal)
        .where(Deal.matched_buyer_id.isnot(None), Deal.ai_processed_at >= start_month)
    )

    closed_this_month = await db.scalar(
        select(func.count()).select_from(Deal).where(Deal.status == "closed", Deal.updated_at >= start_month)
    )

    expected_profit_this_month = await db.scalar(
        select(func.coalesce(func.sum(Deal.expected_profit), 0.0))
        .where(Deal.created_at >= start_month)
    )

    actual_profit_this_month = await db.scalar(
        select(func.coalesce(func.sum(Deal.actual_profit), 0.0))
        .where(Deal.updated_at >= start_month)
    )

    # Conversion rates
    match_rate = (matched_count / total_deals) if total_deals else 0.0
    close_rate_from_matched = (closed_count / matched_count) if matched_count else 0.0

    return {
        "totals": {
            "total_deals": int(total_deals or 0),
            "total_buyers": int(total_buyers or 0),
            "matched_deals": int(matched_count or 0),
            "contacted_deals": int(contacted_count or 0),
            "under_contract_deals": int(under_contract_count or 0),
            "closed_deals": int(closed_count or 0),
        },
        "deals_by_status": deals_by_status,
        "buyers_by_tier": buyers_by_tier,
        "profit": {
            "total_expected_profit": float(total_expected_profit or 0.0),
            "total_assignment_fee": float(total_assignment_fee or 0.0),
            "total_actual_profit": float(total_actual_profit or 0.0),
            "avg_score": float(avg_score or 0.0),
        },
        "this_month": {
            "deals_created": int(deals_created_this_month or 0),
            "matched": int(matched_this_month or 0),
            "closed": int(closed_this_month or 0),
            "expected_profit": float(expected_profit_this_month or 0.0),
            "actual_profit": float(actual_profit_this_month or 0.0),
        },
        "conversion": {
            "match_rate": float(match_rate),
            "close_rate_from_matched": float(close_rate_from_matched),
        },
        "top_cities": top_cities,
        "top_buyers": top_buyers,
    }
