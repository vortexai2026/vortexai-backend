from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# --------------------
# AUTH
# --------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


# --------------------
# BUYERS
# --------------------
class BuyerCreate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    asset_type: str = "real_estate"
    city: Optional[str] = None
    min_budget: float = 0.0
    max_budget: float = 999999999.0


class BuyerOut(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str]
    phone: Optional[str]
    asset_type: str
    city: Optional[str]
    min_budget: float
    max_budget: float

    class Config:
        from_attributes = True


# --------------------
# DEALS
# --------------------
class DealCreate(BaseModel):
    title: str
    asset_type: str = "real_estate"
    city: Optional[str] = None
    price: float
    arv: Optional[float] = None
    repairs: Optional[float] = None
    source: Optional[str] = None
    description: Optional[str] = None


class DealOut(BaseModel):
    id: int
    title: str
    asset_type: str
    city: Optional[str]
    price: float
    arv: Optional[float]
    repairs: Optional[float]
    source: Optional[str]
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# --------------------
# SUBSCRIPTION
# --------------------
class SubscriptionSet(BaseModel):
    tier: str = Field(description="free | pro | elite")


class SubscriptionOut(BaseModel):
    id: int
    buyer_id: int
    tier: str
    active: bool

    class Config:
        from_attributes = True


# --------------------
# MATCHING
# --------------------
class MatchResult(BaseModel):
    deal: DealOut
    score: float


class MatchResponse(BaseModel):
    buyer_id: int
    results: List[MatchResult]
