from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres:XTJGOeohDGvoDAHrvSIfoMkKJCgunrQO@postgres.railway.internal:5432/railway"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()

async def connect_db(retries=5, delay=3):
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(lambda conn: print("✅ Connected to Railway DB"))
            return
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                raise e

@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.get("/")
async def root():
    return {"message": "Vortex AI is running and DB is connected!"}
