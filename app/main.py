from fastapi import FastAPI
from app.routes import router
from app.database import engine, Base

app = FastAPI(title="Vortex AI Backend")


# ---------------- DATABASE STARTUP ----------------
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Connected to Railway DB")


# ---------------- ROOT ----------------
@app.get("/")
async def root():
    return {"message": "Vortex AI is running and DB is connected!"}


# ---------------- INCLUDE ROUTERS ----------------
app.include_router(router)
