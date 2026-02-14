from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer import Buyer


async def reset_monthly_limits(db: AsyncSession):
    """
    Reset monthly match counters for buyers whose reset date has passed.
    """

    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(Buyer).where(
            Buyer.monthly_match_reset_at != None,
            Buyer.monthly_match_reset_at <= now,
        )
    )

    buyers = result.scalars().all()

    for buyer in buyers:
        buyer.monthly_match_count = 0
        buyer.monthly_match_reset_at = now + timedelta(days=30)

        print(f"[RESET] Monthly matches reset for {buyer.email}")
