from fastapi import FastAPI
from database import engine, Base, async_session

app = FastAPI(title="VortexAI")

# Startup event: create tables if they don't exist
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Create tables in DB
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected and tables created")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    print("Database connection closed")

# Simple test route
@app.get("/health")
async def health_check():
    return {"status": "ok"}
