from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/buyers", tags=["Buyers"])


@router.post("/", response_model=schemas.BuyerOut)
async def create_buyer(buyer: schemas.BuyerCreate, db: AsyncSession = Depends(get_db)):

    # 🔒 Prevent duplicate (same phone + city)
    result = await db.execute(
        select(models.Buyer).where(
            models.Buyer.phone == buyer.phone,
            models.Buyer.city == buyer.city
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Buyer already exists")

    new_buyer = models.Buyer(**buyer.dict())
    db.add(new_buyer)
    await db.commit()
    await db.refresh(new_buyer)

    return new_buyer


@router.get("/", response_model=list[schemas.BuyerOut])
async def get_buyers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Buyer))
    return result.scalars().all()
