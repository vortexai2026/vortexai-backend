from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_db
from .models import Buyer, Deal
from .schemas import BuyerCreate, BuyerOut, DealCreate, DealOut
from .matching import match_buyers_to_deal

router = APIRouter()

@router.post("/buyers/", response_model=BuyerOut)
async def create_buyer(buyer: BuyerCreate, db: AsyncSession = Depends(get_db)):
    # OPTIONAL: prevent exact duplicates (simple version)
    # You can strengthen later (unique phone per city, etc.)
    new_buyer = Buyer(**buyer.model_dump())
    db.add(new_buyer)
    await db.commit()
    await db.refresh(new_buyer)
    return new_buyer

@router.get("/buyers/", response_model=list[BuyerOut])
async def get_buyers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Buyer))
    return result.scalars().all()

@router.post("/deals/", response_model=DealOut)
async def create_deal(deal: DealCreate, db: AsyncSession = Depends(get_db)):
    new_deal = Deal(**deal.model_dump())
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)

    await match_buyers_to_deal(db, new_deal)
    return new_deal

@router.get("/deals/", response_model=list[DealOut])
async def get_deals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal))
    return result.scalars().all()
