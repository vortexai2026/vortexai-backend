from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.buyer import Buyer
from app.models.deal import Deal


async def match_buyers(db: AsyncSession, deal: Deal):

    result = await db.execute(
        select(Buyer).where(
            Buyer.status == "active",
            Buyer.market_tag == deal.market_tag,
            Buyer.max_price >= deal.mao
        )
    )

    return list(result.scalars().all())
