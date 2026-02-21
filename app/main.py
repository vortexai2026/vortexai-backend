from fastapi import FastAPI
from app.database import Base, engine
from app.routes import deals_router, buyers_router, autonomous_router

app = FastAPI(title="Vortex AI Backend", version="1.0.0")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # TEMPORARY RESET (fix schema mismatch)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


app.include_router(deals_router)
app.include_router(buyers_router)
app.include_router(autonomous_router)


@app.get("/")
async def root():
    return {"status": "ok"}
