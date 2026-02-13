from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User, Buyer, Deal
from .auth import hash_password

# ---------------- USERS ----------------
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, email: str, password: str):
    new_user = User(email=email, hashed_password=hash_password(password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# ---------------- BUYERS ----------------
async def create_buyer(db: AsyncSession, buyer_data, owner_id: int):
    from .models import Buyer
    new_buyer = Buyer(**buyer_data.dict(), owner_id=owner_id)
    db.add(new_buyer)
    await db.commit()
    await db.refresh(new_buyer)
    return new_buyer

async def get_all_buyers(db: AsyncSession):
    from .models import Buyer
    result = await db.execute(select(Buyer))
    return result.scalars().all()

# ---------------- DEALS ----------------
async def create_deal(db: AsyncSession, deal_data):
    new_deal = Deal(**deal_data.dict())
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)
    return new_deal

async def get_all_deals(db: AsyncSession):
    from .models import Deal
    result = await db.execute(select(Deal))
    return result.scalars().all()
