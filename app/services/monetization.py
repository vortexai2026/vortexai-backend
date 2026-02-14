from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.buyer import Buyer


TIER_LIMITS = {
    "free": 3,
    "pro": 15,
    "elite": None  # unlimited
}


def ensure_monthly_reset(buyer: Buyer):
    now = datetime.now(timezone.utc)

    if (
        buyer.monthly_match_reset_at is None
        or buyer.monthly_match_reset_at.month != now.month
        or buyer.monthly_match_reset_at.year != now.year
    ):
        buyer.monthly_match_count = 0
        buyer.monthly_match_reset_at = now


def can_receive_match(buyer: Buyer):
    limit = TIER_LIMITS.get(buyer.tier, 0)

    if limit is None:
        return True

    return (buyer.monthly_match_count or 0) < limit


def consume_match(buyer: Buyer):
    buyer.monthly_match_count = (buyer.monthly_match_count or 0) + 1
    buyer.total_matches = (buyer.total_matches or 0) + 1


def enforce_match_limit(buyer: Buyer):
    ensure_monthly_reset(buyer)

    if not can_receive_match(buyer):
        raise HTTPException(
            status_code=403,
            detail=f"Monthly match limit reached for tier: {buyer.tier}"
        )

    consume_match(buyer)
