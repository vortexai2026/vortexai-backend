from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal
from app.services.lifecycle_control import set_status


def calculate_mao(deal: Deal) -> float:
    if not deal.arv:
        return 0

    repairs = deal.repair_estimate or 20000
    mao = (deal.arv * 0.70) - repairs
    return round(mao, 2)


async def generate_offer(db: AsyncSession, deal: Deal):
    mao = calculate_mao(deal)

    deal.offer_price = mao
    await db.commit()

    await set_status(db, deal, "OFFER_SENT")

    return {
        "deal_id": deal.id,
        "offer_price": mao,
        "generated_at": datetime.utcnow().isoformat()
    }
