from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.post("/", response_model=schemas.DealOut)
async def create_deal(deal: schemas.DealCreate, db: AsyncSession = Depends(get_db)):

    # 🔒 Prevent duplicate (same title + city)
    result = await db.execute(
        select(models.Deal).where(
            models.Deal.title == deal.title,
            models.Deal.city == deal.city
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Deal already exists")

    new_deal = models.Deal(**deal.dict())
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)

    return new_deal


@router.get("/", response_model=list[schemas.DealOut])
async def get_deals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Deal))
    return result.scalars().all()
