from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.buyer import Buyer
from app.schemas.buyer_import import BuyerImport

router = APIRouter()

@router.post("/buyers/import")
async def import_buyer(payload: BuyerImport, db: AsyncSession = Depends(get_db)):

    buyer = Buyer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        city=payload.city,
        max_price=payload.max_price,
        preferred_zip=payload.preferred_zip,
        rehab_tolerance=payload.rehab_tolerance,
        buy_box_notes=payload.buy_box_notes
    )

    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)

    return {"status": "Buyer imported", "buyer_id": buyer.id}
