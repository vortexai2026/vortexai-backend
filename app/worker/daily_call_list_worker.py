# app/worker/daily_call_list_worker.py

import os
import asyncio

from app.database import async_session_maker
from app.services.daily_call_list_sender import send_daily_call_list

TOP = int(os.getenv("DAILY_CALL_LIST_TOP", "10"))

async def run_once():
    async with async_session_maker() as db:
        return await send_daily_call_list(db, top=TOP)

def main():
    return asyncio.run(run_once())

if __name__ == "__main__":
    main()
