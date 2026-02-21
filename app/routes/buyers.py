from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.buyer import Buyer
from app.schemas.buyer_import import BuyerImport

router = APIRouter(prefix="/buyers", tags=["Buyers"])


@router.post("/import")
async def import_buyer(data: BuyerImport, db: AsyncSession = Depends(get_db)):

    buyer = Buyer(
        name=data.name,
        email=data.email,
        phone=data.phone,
        market_tag=data.market_tag,
        min_price=data.min_price,
        max_price=data.max_price,
        buy_box_beds=data.buy_box_beds,
        buy_box_baths=data.buy_box_baths,
        proof_of_funds=data.proof_of_funds,
        notes=data.notes,
        status="active"
    )

    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)

    return {"status": "success", "buyer_id": buyer.id}
