# app/services/assignment_engine.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal
from app.services.lifecycle_control import set_status


async def assign_deal(db: AsyncSession, deal: Deal, buyer_id: int):
    deal.assigned_buyer_id = buyer_id
    await db.commit()

    await set_status(db, deal, "ASSIGNED")

    return {"assigned": True}
