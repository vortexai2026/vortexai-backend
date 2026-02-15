# app/routes/priority.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.deal import Deal
from app.services.priority_engine import refresh_priorities

router = APIRouter()

@router.post("/priority/refresh")
async def priority_refresh(limit: int = 200, db: AsyncSession = Depends(get_db)):
    return await refresh_priorities(db, limit=limit)

@router.get("/deals/priority")
async def list_priority_deals(top: int = 50, db: AsyncSession = Depends(get_db)):
    q = (
        select(Deal)
        .where(Deal.status.in_(["NEW", "GREEN", "CONTACTED", "FOLLOW_UP", "OFFER_SENT", "UNDER_CONTRACT"]))
        .order_by(desc(Deal.priority_score), desc(Deal.id))
        .limit(top)
    )
    res = await db.execute(q)
    deals = res.scalars().all()

    return {
        "count": len(deals),
        "items": [
            {
                "id": d.id,
                "title": d.title,
                "city": d.city,
                "price": d.price,
                "status": d.status,
                "score": d.score,
                "priority_score": d.priority_score,
                "priority_reason": d.priority_reason,
                "last_contacted_at": getattr(d, "last_contacted_at", None),
            }
            for d in deals
        ]
    }
