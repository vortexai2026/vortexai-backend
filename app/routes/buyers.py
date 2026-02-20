from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.buyer import Buyer

router = APIRouter(prefix="/buyers", tags=["Buyers"])


@router.post("/import")
async def import_buyer(data: dict, db: AsyncSession = Depends(get_db)):

    buyer = Buyer(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        market_tag=data.get("market_tag"),
        min_price=data.get("min_price"),
        max_price=data.get("max_price"),
        buy_box_beds=data.get("buy_box_beds"),
        buy_box_baths=data.get("buy_box_baths"),
        proof_of_funds=data.get("proof_of_funds"),
        notes=data.get("notes")
    )

    db.add(buyer)
    await db.commit()

    return {"message": "Buyer imported"}
