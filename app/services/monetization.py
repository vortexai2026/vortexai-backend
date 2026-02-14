from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.buyer import Buyer


TIER_LIMITS = {
    "free": 3,
    "pro": 15,
    "elite": None  # unlimited
}


def enforce_match_limit(buyer: Buyer):

    now = datetime.now(timezone.utc)

    # Reset monthly counter if needed
    if buyer.monthly_match_reset_at is None or buyer.monthly_match_reset_at.month != now.month:
        buyer.monthly_match_count = 0
        buyer.monthly_match_reset_at = now

    limit = TIER_LIMITS.get(buyer.tier, 0)

    if limit is not None and buyer.monthly_match_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Monthly match limit reached for tier: {buyer.tier}"
        )

    buyer.monthly_match_count += 1
