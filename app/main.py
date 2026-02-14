from fastapi import FastAPI
import asyncio

from app.database import engine, Base
from app.routes import router
from app.worker.autonomous_worker import run_worker


app = FastAPI(title="Vortex AI Backend", version="1.0.0")


async def connect_db(retries=5, delay=2):
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created & DB ready")
            return
        except Exception as e:
            print(f"❌ Attempt {attempt} DB failed: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                raise


@app.on_event("startup")
async def startup_event():
    await connect_db()

    # 🚀 Start autonomous AI worker
    asyncio.create_task(run_worker())
    print("🤖 Autonomous Worker Started")


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Vortex AI Autonomous Operator Running"}


app.include_router(router)
