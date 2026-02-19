import asyncio
from app.database import AsyncSessionLocal
from app.ai.ai_level7_orchestrator import process_once


async def run_once():
    print("🚀 Autonomous loop started")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                print("🔄 Running Level 7 cycle")
                await process_once(db)
                print("✅ Level 7 cycle complete")

        except Exception as e:
            print("❌ Level 7 crash:", e)

        await asyncio.sleep(10)
