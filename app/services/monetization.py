from datetime import datetime, timezone, timedelta

TIER_LIMITS = {
    "free": 3,     # 3 matches per month
    "pro": 50,     # 50 matches per month
    "elite": 9999  # practically unlimited
}


def _month_start(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)


def ensure_monthly_reset(buyer):
    """
    Resets buyer.monthly_match_count at the start of each month.
    buyer.monthly_match_reset_at stores the month start timestamp of last reset.
    """
    now = datetime.now(timezone.utc)
    current_month = _month_start(now)

    if buyer.monthly_match_reset_at is None:
        buyer.monthly_match_reset_at = current_month
        buyer.monthly_match_count = buyer.monthly_match_count or 0
        return

    # If stored reset month is not current month → reset
    last = buyer.monthly_match_reset_at
    last_month = _month_start(last if last.tzinfo else last.replace(tzinfo=timezone.utc))
    if last_month != current_month:
        buyer.monthly_match_reset_at = current_month
        buyer.monthly_match_count = 0


def can_receive_match(buyer) -> tuple[bool, str]:
    tier = (buyer.tier or "free").lower().strip()
    limit = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    used = int(buyer.monthly_match_count or 0)

    if used >= limit:
        return False, f"Tier '{tier}' monthly match limit reached ({used}/{limit})."
    return True, "OK"


def consume_match(buyer):
    buyer.monthly_match_count = int(buyer.monthly_match_count or 0) + 1
