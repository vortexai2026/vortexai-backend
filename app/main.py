from fastapi import FastAPI
from app.database import Base, engine
from app.routes.deals import router as deals_router
from app.routes.buyers import router as buyers_router

app = FastAPI(title="Vortex AI Backend", version="2.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(deals_router)
app.include_router(buyers_router)

@app.get("/")
async def root():
    return {"status": "Vortex AI running"}
