import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.deal import Deal
from app.services.ai_processor import process_deal


POLL_INTERVAL = 10  # seconds


async def run_worker():
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await process_pending_deals(db)
        except Exception as e:
            print(f"[WORKER ERROR] {e}")

        await asyncio.sleep(POLL_INTERVAL)


async def process_pending_deals(db: AsyncSession):
    result = await db.execute(
        select(Deal).where(
            Deal.status.in_(["new", "review", None])
        )
    )

    deals = result.scalars().all()

    for deal in deals:
        try:
            print(f"[WORKER] Processing deal {deal.id}")

            await process_deal(db, deal)

            await db.commit()

        except Exception as e:
            print(f"[WORKER] Deal {deal.id} failed: {e}")
            await db.rollback()
