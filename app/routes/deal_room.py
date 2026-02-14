from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.deal import Deal

router = APIRouter()

@router.get("/deal-room/{token}")
async def get_deal_room(token: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(Deal).where(
            Deal.deal_room_token == token,
            Deal.deal_room_enabled == True
        )
    )

    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return {
        "deal_id": deal.id,
        "title": deal.title,
        "city": deal.city,
        "price": deal.price,
        "arv": deal.arv,
        "repairs": deal.repairs,
        "mao": deal.mao,
        "assignment_fee": deal.assignment_fee,
        "status": deal.status,
        "stripe_payment_status": deal.stripe_payment_status,
        "pay_link": f"/deals/{deal.id}/collect_assignment/{{buyer_id}}"
    }
