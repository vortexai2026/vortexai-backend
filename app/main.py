# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routes.deals import router as deals_router
from app.routes.buyers import router as buyers_router
from app.routes.autonomous import router as autonomous_router

app = FastAPI(title="Vortex AI Backend", version="1.0.0")


@app.on_event("startup")
async def startup():
    # Create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(deals_router)
app.include_router(buyers_router)
app.include_router(autonomous_router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Vortex AI running"}
