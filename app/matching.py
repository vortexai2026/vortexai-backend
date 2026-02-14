from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from .models import Buyer, Deal

async def match_buyers_to_deal(db: AsyncSession, deal: Deal):
    # Find buyers matching city + asset_type + price within budget range
    q = select(Buyer).where(
        and_(
            Buyer.city == deal.city,
            Buyer.asset_type == deal.asset_type,
            Buyer.budget_min <= deal.price,
            Buyer.budget_max >= deal.price,
        )
    )

    result = await db.execute(q)
    buyer = result.scalars().first()

    if buyer:
        deal.matched_buyer_id = buyer.id
        db.add(deal)
        await db.commit()
        await db.refresh(deal)
