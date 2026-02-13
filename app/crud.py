from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Buyer, Deal
from auth import hash_password


# ---------------- USERS ----------------

async def create_user(db: AsyncSession, email: str, password: str):
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


# ---------------- BUYERS ----------------

async def create_buyer(db: AsyncSession, buyer_data, owner_id: int):
    buyer = Buyer(**buyer_data.dict(), owner_id=owner_id)
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return buyer

async def get_all_buyers(db: AsyncSession):
    result = await db.execute(select(Buyer))
    return result.scalars().all()


# ---------------- DEALS ----------------

async def create_deal(db: AsyncSession, deal_data):
    deal = Deal(**deal_data.dict())
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal

async def get_all_deals(db: AsyncSession):
    result = await db.execute(select(Deal))
    return result.scalars().all()
