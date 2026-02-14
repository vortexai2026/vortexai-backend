from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.auth import create_access_token, get_current_user
from app.schemas import (
    UserCreate, Token, UserOut,
    BuyerCreate, BuyerOut,
    DealCreate, DealOut,
    SubscriptionSet, SubscriptionOut,
    MatchResponse, MatchResult
)
from app.matching import rank_deals

router = APIRouter()


# --------------------
# AUTH
# --------------------
@router.post("/auth/register", response_model=UserOut, tags=["Auth"])
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await crud.create_user(db, payload.email, payload.password)
    return user


@router.post("/auth/login", response_model=Token, tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


# --------------------
# BUYER PROFILE
# --------------------
@router.get("/buyers/me", response_model=BuyerOut, tags=["Buyers"])
async def get_my_buyer(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    buyer = await crud.get_buyer_by_user_id(db, user.id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer profile not found. Create it first.")
    return buyer


@router.post("/buyers/me", response_model=BuyerOut, tags=["Buyers"])
async def create_or_update_my_buyer(
    payload: BuyerCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    buyer = await crud.upsert_buyer_for_user(db, user.id, payload.model_dump())
    return buyer


# --------------------
# DEALS
# --------------------
@router.post("/deals", response_model=DealOut, tags=["Deals"])
async def create_deal(payload: DealCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    deal = await crud.create_deal(db, payload.model_dump())
    return deal


@router.get("/deals", response_model=list[DealOut], tags=["Deals"])
async def get_deals(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    deals = await crud.list_deals(db, active_only=True, limit=200)
    return deals


# --------------------
# SUBSCRIPTIONS (Monetization Layer)
# --------------------
@router.get("/billing/me", response_model=SubscriptionOut, tags=["Billing"])
async def my_subscription(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    buyer = await crud.get_buyer_by_user_id(db, user.id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Create buyer profile first (/buyers/me)")

    sub = await crud.ensure_subscription(db, buyer.id)
    return sub


@router.post("/billing/me/tier", response_model=SubscriptionOut, tags=["Billing"])
async def set_my_tier(payload: SubscriptionSet, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    buyer = await crud.get_buyer_by_user_id(db, user.id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Create buyer profile first (/buyers/me)")

    try:
        sub = await crud.set_subscription_tier(db, buyer.id, payload.tier)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return sub


# --------------------
# MATCHING
# --------------------
@router.get("/matching/me", response_model=MatchResponse, tags=["Matching"])
async def match_me(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    buyer = await crud.get_buyer_by_user_id(db, user.id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Create buyer profile first (/buyers/me)")

    deals = await crud.list_deals(db, active_only=True, limit=500)
    ranked = rank_deals(buyer, deals)

    results = []
    for deal, score in ranked[:50]:
        results.append(MatchResult(deal=deal, score=score))

    return MatchResponse(buyer_id=buyer.id, results=results)
