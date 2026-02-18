import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.ai.ai_level7_orchestrator import process_once


async def run_once():
    while True:
        try:
            async with async_session() as db:
                await process_once(db)

        except Exception as e:
            print("❌ Level 7 error:", str(e))

        await asyncio.sleep(10)
