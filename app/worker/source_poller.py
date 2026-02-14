import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services.ingest_engine import ingest_batch


SOURCES_FILE = Path("app/data/sources.json")
POLL_INTERVAL = 60  # seconds


async def load_sources():
    if not SOURCES_FILE.exists():
        return []

    with open(SOURCES_FILE, "r") as f:
        return json.load(f)


async def simulate_fetch_from_source(source):
    """
    Replace this later with real scraper/API logic.
    For now, we simulate incoming deals.
    """

    now = datetime.now(timezone.utc).strftime("%H%M%S")

    return [
        {
            "title": f"{source['name']} Deal {now}",
            "asset_type": source.get("asset_type", "real_estate"),
            "city": source.get("city", "Unknown"),
            "price": 150000,
            "arv": 220000,
            "repairs": 20000,
            "assignment_fee": 10000,
        }
    ]


async def poll_sources():
    print("📡 Source Poller Started")

    while True:
        try:
            sources = await load_sources()

            if not sources:
                await asyncio.sleep(POLL_INTERVAL)
                continue

            async with AsyncSessionLocal() as db:  # type: AsyncSession
                for source in sources:
                    deals = await simulate_fetch_from_source(source)
                    await ingest_batch(db, deals)

        except Exception as e:
            print("❌ Source Poller Error:", e)

        await asyncio.sleep(POLL_INTERVAL)
