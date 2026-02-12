from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, get_db

app = FastAPI()

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root(db: AsyncSession = Depends(get_db)):
    return {"message": "Supabase PostgreSQL is working!"}
