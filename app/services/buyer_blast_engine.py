from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.deal import Deal
from app.models.buyer import Buyer


async def blast_deal_to_buyers(db: AsyncSession, deal: Deal):

    if deal.profit_flag != "green":
        return {"error": "Deal is not green"}

    result = await db.execute(
        select(Buyer).where(
            Buyer.market_tag == deal.market_tag,
            Buyer.max_price >= deal.mao,
            Buyer.status == "active"
        )
    )

    buyers = result.scalars().all()

    return {
        "buyers_matched": len(buyers)
    }
