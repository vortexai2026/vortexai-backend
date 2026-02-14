from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.buyer import Buyer
from app.schemas.buyer import BuyerCreate, BuyerOut

router = APIRouter(prefix="/buyers", tags=["Buyers"])

@router.post("", response_model=BuyerOut)
async def create_buyer(payload: BuyerCreate, db: AsyncSession = Depends(get_db)):
    # prevent duplicates by email
    existing = await db.execute(select(Buyer).where(Buyer.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Buyer email already exists")

    buyer = Buyer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        asset_type=payload.asset_type,
        city=payload.city,
        min_budget=payload.min_budget,
        max_budget=payload.max_budget,
        subscription_tier="free49",
        is_active=False,
    )
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return buyer
