# app/routes/deals.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.deal import Deal

router = APIRouter(prefix="/deals", tags=["deals"])

@router.get("/")
async def list_deals(db: AsyncSession = Depends(get_db), limit: int = 50):
    res = await db.execute(select(Deal).order_by(desc(Deal.created_at)).limit(limit))
    deals = list(res.scalars().all())

    return [
        {
            "id": d.id,
            "created_at": d.created_at,
            "address": d.address,
            "city": d.city,
            "state": d.state,
            "market_tag": d.market_tag,
            "seller_price": d.seller_price,
            "arv_estimated": d.arv_estimated,
            "repair_estimate": d.repair_estimate,
            "mao": d.mao,
            "spread": d.spread,
            "profit_flag": d.profit_flag,
        }
        for d in deals
    ]
