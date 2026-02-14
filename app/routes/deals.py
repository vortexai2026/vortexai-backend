from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Deal, Buyer
from app.schemas import DealCreate, DealOut

router = APIRouter()


@router.post("/", response_model=DealOut)
async def create_deal(deal: DealCreate, db: AsyncSession = Depends(get_db)):
    new_deal = Deal(**deal.dict())
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)

    # Simple auto-match logic
    result = await db.execute(select(Buyer))
    buyers = result.scalars().all()

    for buyer in buyers:
        if (
            buyer.city.lower() == deal.city.lower()
            and buyer.asset_type.lower() == deal.asset_type.lower()
            and buyer.budget_min <= deal.price <= buyer.budget_max
        ):
            new_deal.matched_buyer_id = buyer.id
            await db.commit()
            break

    return new_deal


@router.get("/", response_model=list[DealOut])
async def get_deals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal))
    return result.scalars().all()
