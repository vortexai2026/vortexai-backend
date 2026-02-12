from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Buyer, Deal, Match


async def match_buyers_to_deal(db: AsyncSession, deal: Deal):
    """
    Auto matches a deal to all buyers who qualify.
    """
    query = select(Buyer).where(
        Buyer.is_active == True,
        Buyer.city.ilike(deal.city),
        Buyer.asset_type.ilike(deal.asset_type),
        Buyer.min_budget <= deal.price,
        Buyer.max_budget >= deal.price
    )

    result = await db.execute(query)
    buyers = result.scalars().all()

    matches_created = []

    for buyer in buyers:
        existing_match_query = select(Match).where(
            Match.buyer_id == buyer.id,
            Match.deal_id == deal.id
        )
        existing_match_result = await db.execute(existing_match_query)
        existing_match = existing_match_result.scalar_one_or_none()

        if not existing_match:
            new_match = Match(buyer_id=buyer.id, deal_id=deal.id)
            db.add(new_match)
            matches_created.append(new_match)

    await db.commit()
    return matches_created
