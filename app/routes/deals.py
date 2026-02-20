from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal
from app.services.scoring import score_deal

router = APIRouter(prefix="/deals", tags=["Deals"])

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
        seller_name=data.get("seller_name"),
        seller_phone=data.get("seller_phone"),
        seller_email=data.get("seller_email"),
        source=data.get("source"),
        listing_url=data.get("listing_url"),
        status="Lead",
    )

    deal = score_deal(deal)  # score immediately on create

    db.add(deal)
    await db.commit()
    await db.refresh(deal)

    return {"message": "Deal created", "deal_id": deal.id, "profit_flag": deal.profit_flag}

@router.get("/")
async def list_deals(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Deal).order_by(Deal.id.desc()).limit(200))
    deals = list(res.scalars().all())

    return [
        {
            "id": d.id,
            "address": d.address,
            "city": d.city,
            "state": d.state,
            "zip_code": d.zip_code,
            "seller_price": d.seller_price,
            "arv_estimated": d.arv_estimated,
            "repair_estimate": d.repair_estimate,
            "mao": d.mao,
            "spread": d.spread,
            "confidence_score": d.confidence_score,
            "profit_flag": d.profit_flag,
            "market_tag": d.market_tag,
            "source": d.source,
            "listing_url": d.listing_url,
        }
        for d in deals
    ]
