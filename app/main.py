from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import engine, Base, get_db
from .crud import create_user, get_users, get_user
from .schemas import UserCreate, UserResponse

app = FastAPI(title="VortexAI Backend")

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "✅ Supabase PostgreSQL is working!"}

# Create new user
@app.post("/users", response_model=UserResponse)
async def api_create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user.name, user.email)

# Get all users
@app.get("/users", response_model=list[UserResponse])
async def api_get_users(db: AsyncSession = Depends(get_db)):
    return await get_users(db)

# Get user by ID
@app.get("/users/{user_id}", response_model=UserResponse)
async def api_get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
