from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models.deal import Deal

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("/")
async def list_deals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal))
    deals = result.scalars().all()

    return [
        {
            "id": d.id,
            "address": d.address,
            "city": d.city,
            "state": d.state,
            "zip_code": d.zip_code,
            "beds": d.beds,
            "baths": d.baths,
            "sqft": d.sqft,
            "year_built": d.year_built,
            "seller_price": d.seller_price,
            "arv_estimated": d.arv_estimated,
            "repair_estimate": d.repair_estimate,
            "spread": d.spread,
            "profit_flag": d.profit_flag,
            "market_tag": d.market_tag
        }
        for d in deals
    ]


@router.post("/create")
async def create_deal(data: dict, db: AsyncSession = Depends(get_db)):
    deal = Deal(
        address=data.get("address"),
        city=data.get("city"),
        state=data.get("state"),
        zip_code=data.get("zip_code"),
        beds=data.get("beds"),
        baths=data.get("baths"),
        sqft=data.get("sqft"),
        year_built=data.get("year_built"),
        seller_price=data.get("seller_price"),
        notes=data.get("notes"),
        status="Lead"
    )

    db.add(deal)
    await db.commit()
    await db.refresh(deal)

    return {
        "message": "Deal created",
        "deal_id": deal.id
    }
