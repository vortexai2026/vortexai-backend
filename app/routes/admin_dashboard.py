from fastapi import APIRouter
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.deal import Deal
from app.models.buyer import Buyer
from app.models.buyer_interest import BuyerInterest

router = APIRouter()


@router.get("/admin/deals")
async def get_all_deals():

    async with AsyncSessionLocal() as db:

        result = await db.execute(select(Deal))
        deals = result.scalars().all()

        output = []

        for deal in deals:

            # Count interest
            interest_count = await db.scalar(
                select(func.count())
                .select_from(BuyerInterest)
                .where(BuyerInterest.deal_id == deal.id)
            )

            matched_buyer_email = None
            if deal.matched_buyer_id:
                buyer = await db.get(Buyer, deal.matched_buyer_id)
                if buyer:
                    matched_buyer_email = buyer.email

            output.append({
                "deal_id": deal.id,
                "title": deal.title,
                "city": deal.city,
                "asset_type": deal.asset_type,
                "price": deal.price,
                "score": deal.score,
                "ai_decision": deal.ai_decision,
                "status": deal.status,
                "expected_profit": deal.expected_profit,
                "actual_profit": deal.actual_profit,
                "matched_buyer": matched_buyer_email,
                "interest_count": interest_count or 0,
            })

        return {
            "total_deals": len(output),
            "deals": output
        }
