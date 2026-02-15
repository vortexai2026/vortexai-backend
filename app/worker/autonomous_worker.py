# app/worker/autonomous_worker.py

import os
import asyncio
from app.database import async_session_maker
from app.services.execution_pipeline import run_autonomous_cycle

CYCLE_LIMIT = int(os.getenv("AUTO_CYCLE_LIMIT", "10"))
RUN_ON_STARTUP = os.getenv("AUTO_RUN_ON_STARTUP", "false").lower() == "true"

async def run_once():
    async with async_session_maker() as db:
        return await run_autonomous_cycle(db, limit=CYCLE_LIMIT)

def run_worker():
    """
    Safe entry point if you want to call it from main.py or a separate worker container.
    """
    return asyncio.run(run_once())

# Optional: if you have a worker container that just runs this file
if __name__ == "__main__":
    asyncio.run(run_once())
