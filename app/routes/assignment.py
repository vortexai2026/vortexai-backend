from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.deal import Deal
from app.models.buyer import Buyer
from app.services.assignment_contract_engine import generate_assignment_contract

router = APIRouter()

@router.post("/deals/{deal_id}/assign/{buyer_id}")
async def assign_deal(
    deal_id: int,
    buyer_id: int,
    db: AsyncSession = Depends(get_db)
):
    deal_result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = deal_result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    buyer_result = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    buyer = buyer_result.scalar_one_or_none()

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    contract_data = generate_assignment_contract(deal, buyer)

    deal.status = "ASSIGNED"
    deal.actual_profit = deal.assignment_fee or 15000

    await db.commit()

    return {
        "message": "Deal assigned successfully",
        "contract_preview": contract_data
    }
