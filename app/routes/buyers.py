# app/routes/buyers.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.buyer import Buyer
from app.schemas.buyer_import import BuyerImport

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.get("/")
async def list_buyers(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Buyer).order_by(Buyer.id.desc()).limit(200))
    buyers = list(res.scalars().all())
    return [
        {
            "id": b.id,
            "name": b.name,
            "email": b.email,
            "phone": b.phone,
            "market_tag": b.market_tag,
            "min_price": b.min_price,
            "max_price": b.max_price,
            "tier": b.tier,
            "status": b.status,
        }
        for b in buyers
    ]


@router.post("/import")
async def import_buyer(payload: BuyerImport, db: AsyncSession = Depends(get_db)):
    buyer = Buyer(
        name=payload.name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        market_tag=payload.market_tag,
        min_price=payload.min_price,
        max_price=payload.max_price,
        buy_box_beds=payload.buy_box_beds,
        buy_box_baths=payload.buy_box_baths,
        proof_of_funds=payload.proof_of_funds,
        notes=payload.notes,
        tier=payload.tier or "free",
        status=payload.status or "active",
        is_active=True,
    )
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return {"message": "Buyer imported", "id": buyer.id}
