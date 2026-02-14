from fastapi import FastAPI
from app.routes import router   # IMPORTANT
from app.database import engine, Base
import asyncio

app = FastAPI(title="Vortex AI Backend")


# Startup DB
async def connect_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Connected to Railway DB")


@app.on_event("startup")
async def startup_event():
    await connect_db()


# Root
@app.get("/")
async def root():
    return {"message": "Vortex AI is running and DB is connected!"}


# VERY IMPORTANT LINE
app.include_router(router)
