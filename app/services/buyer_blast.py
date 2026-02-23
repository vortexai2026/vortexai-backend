# app/services/buyer_blast.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal

async def blast_green_deals(db: AsyncSession, deal: Deal) -> int:
    """
    TEMP: we are skipping buyer blasts for now.
    Later we connect buyer_matcher + email/sms.
    """
    return 0
