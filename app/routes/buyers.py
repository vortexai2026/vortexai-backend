from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.buyer import Buyer
from app.schemas.buyer_import import BuyerImport

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.post("/import")
async def import_buyer(payload: BuyerImport, db: AsyncSession = Depends(get_db)):
    # Avoid duplicates by email
    res = await db.execute(select(Buyer).where(Buyer.email == payload.email))
    existing = res.scalar_one_or_none()
    if existing:
        # update existing buyer (safe and fast)
        existing.name = payload.name
        existing.asset_type = payload.asset_type
        existing.city = payload.city
        existing.max_budget = payload.max_budget
        existing.preferred_zip = payload.preferred_zip
        existing.rehab_tolerance = payload.rehab_tolerance
        existing.buy_box_notes = payload.buy_box_notes
        existing.phone = payload.phone

        await db.commit()
        await db.refresh(existing)
        return {"status": "updated", "buyer_id": existing.id}

    buyer = Buyer(
        email=payload.email,
        name=payload.name,
        asset_type=payload.asset_type,
        city=payload.city,
        max_budget=payload.max_budget,
        preferred_zip=payload.preferred_zip,
        rehab_tolerance=payload.rehab_tolerance,
        buy_box_notes=payload.buy_box_notes,
        phone=payload.phone,
    )

    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)

    return {"status": "created", "buyer_id": buyer.id}
