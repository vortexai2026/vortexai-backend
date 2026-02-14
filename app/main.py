from fastapi import FastAPI
import asyncio

from app.database import engine, Base
from app.routes import router
from app.worker.autonomous_worker import run_worker
from app.worker.source_poller import poll_sources

app = FastAPI(title="Vortex AI Backend", version="1.0.0")


async def connect_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created & DB ready")


@app.on_event("startup")
async def startup_event():
    await connect_db()

    # Start AI worker
    asyncio.create_task(run_worker())

    # Start source poller
    asyncio.create_task(poll_sources())


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Vortex AI is fully autonomous."}


app.include_router(router)
