from fastapi import FastAPI
from database import engine, Base, async_session

app = FastAPI(title="Vortex AI Backend")

# Example root endpoint
@app.get("/")
async def root():
    return {"status": "ok"}

# Optional: initialize database on startup
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Create tables if not exist
        await conn.run_sync(Base.metadata.create_all)
