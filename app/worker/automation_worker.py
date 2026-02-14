import os
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.deal import Deal
from app.services.ai_processor import process_deal


SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "10"))
BATCH_SIZE = int(os.getenv("WORKER_BATCH_SIZE", "5"))
MAX_RETRIES = int(os.getenv("WORKER_MAX_RETRIES", "3"))


async def fetch_pending_deals(db: AsyncSession):
    result = await db.execute(
        select(Deal)
        .where(Deal.status == "new")
        .order_by(Deal.created_at.asc())
        .limit(BATCH_SIZE)
    )
    return result.scalars().all()


async def process_single_deal(db: AsyncSession, deal: Deal):
    try:
        result = await process_deal(db, deal)
        await db.commit()
        print(f"✅ Deal {deal.id} processed → {result.get('status')}")
        return True
    except Exception as e:
        await db.rollback()
        print(f"❌ Error processing deal {deal.id}: {e}")
        return False


async def worker_loop():
    print("🤖 Vortex AI Worker Started")
    print(f"Interval: {SLEEP_SECONDS}s | Batch: {BATCH_SIZE}")

    while True:
        try:
            async with AsyncSessionLocal() as db:

                deals = await fetch_pending_deals(db)

                if not deals:
                    await asyncio.sleep(SLEEP_SECONDS)
                    continue

                print(f"🔎 Found {len(deals)} new deals")

                for deal in deals:

                    retries = 0
                    success = False

                    while retries < MAX_RETRIES and not success:
                        success = await process_single_deal(db, deal)
                        retries += 1

                    if not success:
                        deal.status = "failed"
                        await db.commit()
                        print(f"🔥 Deal {deal.id} marked as failed after retries")

        except Exception as loop_error:
            print(f"🔥 Worker Loop Critical Error: {loop_error}")

        await asyncio.sleep(SLEEP_SECONDS)


def main():
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
