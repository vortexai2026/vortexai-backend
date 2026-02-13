from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import engine, Base, get_db
import models
import schemas
import crud
from auth import verify_password, create_access_token
import asyncio

app = FastAPI()


# ---------------- STARTUP (CREATE TABLES) ----------------

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

@app.get("/")
async def root():
    return {"message": "Vortex AI Backend Running 🚀"}


# ---------------- SIGNUP ----------------

@app.post("/signup")
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = await crud.create_user(db, user.email, user.password)
    return {"message": "User created", "user_id": new_user.id}


# ---------------- LOGIN ----------------

@app.post("/login")
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user.email)

    if not existing:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, existing.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": existing.email, "user_id": existing.id})

    return {"access_token": token, "token_type": "bearer"}


# ---------------- CREATE BUYER ----------------

@app.post("/buyers")
async def create_buyer(
    buyer: schemas.BuyerCreate,
    owner_id: int,
    db: AsyncSession = Depends(get_db)
):
    new_buyer = await crud.create_buyer(db, buyer, owner_id)
    return {"message": "Buyer created", "buyer": new_buyer.id}


# ---------------- LIST BUYERS ----------------

@app.get("/buyers")
async def list_buyers(db: AsyncSession = Depends(get_db)):
    buyers = await crud.get_all_buyers(db)
    return buyers


# ---------------- CREATE DEAL ----------------

@app.post("/deals")
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

@app.get("/deals")
async def list_deals(db: AsyncSession = Depends(get_db)):
    deals = await crud.get_all_deals(db)
    return deals
