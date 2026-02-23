from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db import get_session
from app.models.deal_room import DealRoomToken
from app.models.deal import Deal

router = APIRouter(prefix="/deal-room", tags=["Deal Room"])

@router.get("/{token}")
async def get_deal_room(token: str, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(DealRoomToken).where(DealRoomToken.token == token).limit(1))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Invalid token")

    # expiry check
    if datetime.now(timezone.utc) > t.expires_at:
        raise HTTPException(status_code=410, detail="Token expired")

    dres = await session.execute(select(Deal).where(Deal.id == t.deal_id).limit(1))
    deal = dres.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return {
        "deal_id": deal.id,
        "property_address": deal.property_address,
        "city": deal.city,
        "state": deal.state,
        "zip": deal.zip,
        "arv": float(deal.arv) if deal.arv is not None else None,
        "repairs": float(deal.repairs) if deal.repairs is not None else None,
        "offer_price": float(deal.offer_price) if deal.offer_price is not None else None,
        "estimated_spread": float(deal.estimated_spread) if deal.estimated_spread is not None else None,
        "status": deal.status,
        "notes": deal.notes,
    }
