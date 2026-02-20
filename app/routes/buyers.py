from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.buyer import Buyer

router = APIRouter(prefix="/buyers", tags=["Buyers"])

@router.post("/create")
async def create_buyer(data: dict, db: AsyncSession = Depends(get_db)):
    b = Buyer(
        name=data.get("name"),
        phone=data.get("phone"),
        email=data.get("email"),
        market_tag=data.get("market_tag"),
        max_price=data.get("max_price"),
        buy_type=data.get("buy_type", "both"),
        preferred_zip=data.get("preferred_zip"),
        proof_of_funds=bool(data.get("proof_of_funds", False)),
        notes=data.get("notes"),
    )
    db.add(b)
    await db.commit()
    await db.refresh(b)
    return {"message": "Buyer created", "buyer_id": b.id}

@router.post("/import")
async def import_buyers(payload: dict, db: AsyncSession = Depends(get_db)):
    """
    payload format:
    { "buyers": [ {buyer1}, {buyer2}, ... ] }
    """
    buyers = payload.get("buyers", [])
    created = 0
    for data in buyers:
        b = Buyer(
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email"),
            market_tag=data.get("market_tag"),
            max_price=data.get("max_price"),
            buy_type=data.get("buy_type", "both"),
            preferred_zip=data.get("preferred_zip"),
            proof_of_funds=bool(data.get("proof_of_funds", False)),
            notes=data.get("notes"),
        )
        db.add(b)
        created += 1
    await db.commit()
    return {"message": "Buyers imported", "count": created}

@router.get("/")
async def list_buyers(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Buyer).order_by(Buyer.id.desc()).limit(500))
    buyers = list(res.scalars().all())
    return [
        {
            "id": b.id,
            "name": b.name,
            "phone": b.phone,
            "email": b.email,
            "market_tag": b.market_tag,
            "max_price": b.max_price,
            "buy_type": b.buy_type,
            "proof_of_funds": b.proof_of_funds,
        }
        for b in buyers
    ]
