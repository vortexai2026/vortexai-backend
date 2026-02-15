from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Deal

router = APIRouter(prefix="/seller-calls", tags=["Seller Calls"])


@router.get("/{deal_id}")
async def get_deal(deal_id: int, db: AsyncSession = Depends(get_db)):

    # ✅ await is inside async function
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id)
    )

    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return deal
