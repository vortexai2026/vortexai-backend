from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import engine, Base, get_db
from .crud import create_user, get_users, get_user

app = FastAPI(title="VortexAI Backend")

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Test root endpoint
@app.get("/")
async def root():
    return {"message": "Supabase PostgreSQL is working!"}

# Create new user
@app.post("/users")
async def api_create_user(name: str, email: str, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, name, email)
    return user

# Get all users
@app.get("/users")
async def api_get_users(db: AsyncSession = Depends(get_db)):
    users = await get_users(db)
    return users

# Get user by ID
@app.get("/users/{user_id}")
async def api_get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
