import os
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal  # must exist in your database.py
from app.models.deal import Deal
from app.services.ai_processor import process_deal


SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "10"))
BATCH_SIZE = int(os.getenv("WORKER_BATCH_SIZE", "10"))


async def fetch_new_deals(db: AsyncSession):
    # Only deals not processed yet
    res = await db.execute(
        select(Deal)
        .where(Deal.status == "new")
        .order_by(Deal.created_at.asc())
        .limit(BATCH_SIZE)
    )
    return res.scalars().all()


async def worker_loop():
    print("🤖 Vortex AI Worker started")
    print(f"⏱ sleep={SLEEP_SECONDS}s batch={BATCH_SIZE}")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                deals = await fetch_new_deals(db)

                if not deals:
                    print("✅ No new deals. sleeping...")
                    await asyncio.sleep(SLEEP_SECONDS)
                    continue

                print(f"🔎 Found {len(deals)} new deals")

                for deal in deals:
                    try:
                        result = await process_deal(db, deal)
                        await db.commit()
                        print(f"✅ processed deal {deal.id}: {result.get('status')} decision={result.get('decision')}")
                    except Exception as e:
                        await db.rollback()
                        # mark dead only if you want; for now just log
                        print(f"❌ deal {deal.id} failed: {e}")

        except Exception as e:
            print(f"🔥 Worker loop error: {e}")

        await asyncio.sleep(SLEEP_SECONDS)


def main():
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
