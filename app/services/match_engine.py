# app/services/match_engine.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.buyer import Buyer


async def match_deal_to_buyer(
    db: AsyncSession,
    deal: Deal,
) -> bool:
    """
    Match a newly created deal to the first eligible buyer.
    Returns True if matched, False otherwise.
    """

    if deal.status != "new":
        return False

    # Find eligible buyers
    result = await db.execute(
        select(Buyer).where(
            Buyer.asset_type == deal.asset_type,
            Buyer.city == deal.city,
            Buyer.max_budget >= deal.price,
            Buyer.is_active == True,
        )
    )

    buyers = result.scalars().all()

    if not buyers:
        return False

    # Take first buyer (later we can improve prioritization)
    buyer = buyers[0]

    # Update deal
    deal.status = "matched"
    deal.matched_buyer_id = buyer.id

    # Update buyer stats
    buyer.total_matches += 1

    return True
