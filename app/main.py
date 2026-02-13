from fastapi import FastAPI
from app.routes import router
from app.database import engine, Base
import asyncio

app = FastAPI(title="Vortex AI Backend", version="0.1.0")

# ---------------- STARTUP ----------------
async def connect_db(retries=5, delay=3):
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
                raise e

@app.on_event("startup")
async def startup_event():
    await connect_db()

# ---------------- ROOT ----------------
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Vortex AI is running and DB is connected!"}

# ---------------- INCLUDE ROUTER ----------------
app.include_router(router)
