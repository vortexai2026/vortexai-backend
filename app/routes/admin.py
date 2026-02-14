from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone

from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer

router = APIRouter(tags=["Admin"])


@router.get("/admin/metrics")
async def get_admin_metrics(db: AsyncSession = Depends(get_db)):

    # Total Deals
    total_deals = await db.scalar(select(func.count()).select_from(Deal))

    # Deals by status
    deals_by_status_query = await db.execute(
        select(Deal.status, func.count()).group_by(Deal.status)
    )
    deals_by_status = {
        status: count for status, count in deals_by_status_query.all()
    }

    # Total Buyers
    total_buyers = await db.scalar(select(func.count()).select_from(Buyer))

    # Buyers by tier
    buyers_by_tier_query = await db.execute(
        select(Buyer.tier, func.count()).group_by(Buyer.tier)
    )
    buyers_by_tier = {
        tier: count for tier, count in buyers_by_tier_query.all()
    }

    # Profit metrics
    total_expected_profit = await db.scalar(
        select(func.coalesce(func.sum(Deal.expected_profit), 0.0))
    )

    total_actual_profit = await db.scalar(
        select(func.coalesce(func.sum(Deal.actual_profit), 0.0))
    )

    # Matches this month
    now = datetime.now(timezone.utc)
    start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    matches_this_month = await db.scalar(
        select(func.count())
        .select_from(Deal)
        .where(
            Deal.matched_buyer_id.isnot(None),
            Deal.ai_processed_at >= start_of_month
        )
    )

    # Top cities
    top_cities_query = await db.execute(
        select(Deal.city, func.count())
        .group_by(Deal.city)
        .order_by(func.count().desc())
        .limit(5)
    )

    top_cities = [
        {"city": city, "deal_count": count}
        for city, count in top_cities_query.all()
    ]

    return {
        "total_deals": total_deals,
        "deals_by_status": deals_by_status,
        "total_buyers": total_buyers,
        "buyers_by_tier": buyers_by_tier,
        "total_expected_profit": float(total_expected_profit or 0),
        "total_actual_profit": float(total_actual_profit or 0),
        "matches_this_month": matches_this_month,
        "top_cities": top_cities
    }
