from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.services.lifecycle_control import set_status


async def generate_assignment_contract(
    db: AsyncSession,
    deal: Deal,
    buyer_id: int,
    assignment_fee: float
):
    """
    Generates assignment contract data.
    You can later convert this into PDF.
    """

    deal.assigned_buyer_id = buyer_id
    deal.assignment_fee = assignment_fee
    deal.assignment_date = datetime.utcnow()

    await db.commit()

    await set_status(db, deal, "ASSIGNED")

    return {
        "deal_id": deal.id,
        "buyer_id": buyer_id,
        "assignment_fee": assignment_fee,
        "status": "ASSIGNED"
    }
