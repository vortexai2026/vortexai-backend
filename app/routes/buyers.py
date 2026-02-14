from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Buyer
from app.schemas import BuyerCreate, BuyerOut

router = APIRouter(tags=["Buyers"])


@router.post("/buyers", response_model=BuyerOut)
async def create_buyer(buyer: BuyerCreate, db: AsyncSession = Depends(get_db)):
    new_buyer = Buyer(**buyer.dict())
    db.add(new_buyer)
    await db.commit()
    await db.refresh(new_buyer)
    return new_buyer


@router.get("/buyers", response_model=list[BuyerOut])
async def get_buyers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Buyer))
    return result.scalars().all()
