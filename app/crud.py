from typing import Optional, List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Buyer, Deal, Subscription
from app.auth import hash_password, verify_password


# --------------------
# USERS
# --------------------
async def create_user(db: AsyncSession, email: str, password: str) -> User:
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# --------------------
# BUYERS
# --------------------
async def upsert_buyer_for_user(db: AsyncSession, user_id: int, data: dict) -> Buyer:
    res = await db.execute(select(Buyer).where(Buyer.user_id == user_id))
    buyer = res.scalar_one_or_none()

    if buyer:
        for k, v in data.items():
            setattr(buyer, k, v)
        await db.commit()
        await db.refresh(buyer)
        return buyer

    buyer = Buyer(user_id=user_id, **data)
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)

    # Ensure subscription exists
    await ensure_subscription(db, buyer.id)
    return buyer


async def get_buyer_by_user_id(db: AsyncSession, user_id: int) -> Optional[Buyer]:
    res = await db.execute(select(Buyer).where(Buyer.user_id == user_id))
    return res.scalar_one_or_none()


async def get_buyer_by_id(db: AsyncSession, buyer_id: int) -> Optional[Buyer]:
    res = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    return res.scalar_one_or_none()


# --------------------
# DEALS
# --------------------
async def create_deal(db: AsyncSession, data: dict) -> Deal:
    deal = Deal(**data)
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


async def list_deals(db: AsyncSession, active_only: bool = True, limit: int = 100) -> List[Deal]:
    q = select(Deal)
    if active_only:
        q = q.where(Deal.is_active == True)  # noqa
    q = q.order_by(Deal.created_at.desc()).limit(limit)
    res = await db.execute(q)
    return list(res.scalars().all())


async def get_deal_by_id(db: AsyncSession, deal_id: int) -> Optional[Deal]:
    res = await db.execute(select(Deal).where(Deal.id == deal_id))
    return res.scalar_one_or_none()


# --------------------
# SUBSCRIPTION
# --------------------
async def ensure_subscription(db: AsyncSession, buyer_id: int) -> Subscription:
    res = await db.execute(select(Subscription).where(Subscription.buyer_id == buyer_id))
    sub = res.scalar_one_or_none()
    if sub:
        return sub

    sub = Subscription(buyer_id=buyer_id, tier="free", active=True)
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


async def get_subscription(db: AsyncSession, buyer_id: int) -> Optional[Subscription]:
    res = await db.execute(select(Subscription).where(Subscription.buyer_id == buyer_id))
    return res.scalar_one_or_none()


async def set_subscription_tier(db: AsyncSession, buyer_id: int, tier: str) -> Subscription:
    tier = tier.lower().strip()
    if tier not in ("free", "pro", "elite"):
        raise ValueError("Tier must be: free | pro | elite")

    sub = await ensure_subscription(db, buyer_id)
    sub.tier = tier
    await db.commit()
    await db.refresh(sub)
    return sub
