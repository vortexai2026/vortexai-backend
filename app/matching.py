from sqlalchemy.ext.asyncio import AsyncSession
from .crud import get_all_buyers
from .models import Deal

async def match_buyers_to_deal(db: AsyncSession, deal: Deal):
    buyers = await get_all_buyers(db)
    for buyer in buyers:
        if (
            buyer.city.lower() == deal.city.lower()
            and buyer.asset_type.lower() == deal.asset_type.lower()
            and buyer.budget_min <= deal.price <= buyer.budget_max
        ):
            deal.matched_buyer_id = buyer.id
            db.add(deal)
            await db.commit()
            await db.refresh(deal)
            break
