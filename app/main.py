from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, engine, Base
import models, schemas, crud
from auth import verify_password, create_access_token
import asyncio
from typing import List

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

@app.get("/", response_model=dict)
async def root():
    return {"message": "Vortex AI is running and DB is connected!"}


# ---------------- SIGNUP ----------------

@app.post("/signup", response_model=dict)
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    new_user = await crud.create_user(db, user.email, user.password)
    return {"message": "User created", "user_id": new_user.id}


# ---------------- LOGIN ----------------

@app.post("/login", response_model=dict)
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user.email)
    if not existing or not verify_password(user.password, existing.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": existing.email, "user_id": existing.id})
    return {"access_token": token, "token_type": "bearer"}


# ---------------- CREATE BUYER ----------------

@app.post("/buyers", response_model=dict)
async def create_buyer(
    buyer: schemas.BuyerCreate,
    owner_id: int,
    db: AsyncSession = Depends(get_db)
):
    new_buyer = await crud.create_buyer(db, buyer, owner_id)
    return {"message": "Buyer created", "buyer_id": new_buyer.id}


# ---------------- LIST BUYERS ----------------

@app.get("/buyers", response_model=List[schemas.BuyerCreate])
async def list_buyers(db: AsyncSession = Depends(get_db)):
    buyers = await crud.get_all_buyers(db)
    return buyers


# ---------------- CREATE DEAL ----------------

@app.post("/deals", response_model=dict)
async def create_deal(deal: schemas.DealCreate, db: AsyncSession = Depends(get_db)):
    new_deal = await crud.create_deal(db, deal)

    # AUTO MATCH LOGIC
    buyers = await crud.get_all_buyers(db)
    for buyer in buyers:
        if (
            buyer.city.lower() == deal.city.lower()
            and buyer.asset_type.lower() == deal.asset_type.lower()
            and buyer.budget_min <= deal.price <= buyer.budget_max
        ):
            new_deal.matched_buyer_id = buyer.id
            await db.commit()
            break

    return {"message": "Deal created", "deal_id": new_deal.id, "matched_buyer_id": new_deal.matched_buyer_id}


# ---------------- LIST DEALS ----------------

@app.get("/deals", response_model=List[schemas.DealCreate])
async def list_deals(db: AsyncSession = Depends(get_db)):
    deals = await crud.get_all_deals(db)
    return deals
