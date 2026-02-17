import asyncio
from app.ai.ai_level7_orchestrator import process_once


async def run_once():
    while True:
        try:
            await process_once()
        except Exception as e:
            print("❌ Level 7 error:", e)

        await asyncio.sleep(10)
