from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.buyer import Buyer
from app.models.deal import Deal

async def match_buyers_for_deal(db: AsyncSession, deal: Deal, limit: int = 100) -> list[Buyer]:
    target_price = deal.mao or deal.seller_price or 0

    q = (
        select(Buyer)
        .where(
            Buyer.market_tag == deal.market_tag,
            or_(Buyer.max_price == None, Buyer.max_price >= target_price),
        )
        .limit(limit)
    )

    res = await db.execute(q)
    return list(res.scalars().all())
