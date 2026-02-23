from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.buyer import Buyer
from app.schemas.buyer import BuyerCreateIn

router = APIRouter(prefix="/buyers", tags=["Buyers"])

@router.post("/create")
async def create_buyer(payload: BuyerCreateIn, session: AsyncSession = Depends(get_session)):
    b = Buyer(**payload.model_dump())
    session.add(b)
    await session.commit()
    await session.refresh(b)
    return {"ok": True, "buyer_id": b.id}

@router.get("/")
async def list_buyers(session: AsyncSession = Depends(get_session)):
    # MVP: simple list
    from sqlalchemy import select
    res = await session.execute(select(Buyer).limit(200))
    buyers = res.scalars().all()
    return [{
        "id": x.id, "name": x.name, "email": x.email, "tier": x.tier, "score": x.score,
        "city": x.city, "state": x.state
    } for x in buyers]
