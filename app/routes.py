from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Buyer, Deal, Match
from app.schemas import BuyerCreate, BuyerOut, DealCreate, DealOut, MatchOut
from app.matching import match_buyers_to_deal

router = APIRouter()


# ---------------- BUYERS ----------------

@router.post("/buyers", response_model=BuyerOut)
async def create_buyer(buyer: BuyerCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Buyer).where(Buyer.email == buyer.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Buyer already exists")

    new_buyer = Buyer(**buyer.dict())
    db.add(new_buyer)
    await db.commit()
    await db.refresh(new_buyer)
    return new_buyer


@router.get("/buyers", response_model=list[BuyerOut])
async def get_buyers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Buyer))
    return result.scalars().all()


# ---------------- DEALS ----------------

@router.post("/deals", response_model=DealOut)
async def create_deal(deal: DealCreate, db: AsyncSession = Depends(get_db)):
    new_deal = Deal(**deal.dict())
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)

    # AUTO MATCH
    await match_buyers_to_deal(db, new_deal)

    return new_deal


@router.get("/deals", response_model=list[DealOut])
async def get_deals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal))
    return result.scalars().all()


# ---------------- MATCHES ----------------

@router.get("/matches", response_model=list[MatchOut])
async def get_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match))
    return result.scalars().all()
