import os
import asyncio
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.deal import Deal
from app.services.ai_processor import process_deal


SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "10"))
BATCH_SIZE = int(os.getenv("WORKER_BATCH_SIZE", "10"))


async def fetch_new_deals(db):
    result = await db.execute(
        select(Deal)
        .where(Deal.status == "new")
        .order_by(Deal.created_at.asc())
        .limit(BATCH_SIZE)
    )
    return result.scalars().all()


async def worker_loop():
    print("🤖 Vortex AI Automation Worker Started")
    print(f"⏱ Poll interval: {SLEEP_SECONDS}s | Batch size: {BATCH_SIZE}")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                deals = await fetch_new_deals(db)

                if not deals:
                    print("🟢 No new deals found")
                    await asyncio.sleep(SLEEP_SECONDS)
                    continue

                print(f"🔎 Found {len(deals)} new deals")

                for deal in deals:
                    try:
                        result = await process_deal(db, deal)
                        await db.commit()
                        print(f"✅ Deal {deal.id} processed → {result.get('status')}")
                    except Exception as e:
                        await db.rollback()
                        print(f"❌ Failed processing deal {deal.id}: {e}")

        except Exception as e:
            print(f"🔥 Worker Loop Error: {e}")

        await asyncio.sleep(SLEEP_SECONDS)


def main():
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
