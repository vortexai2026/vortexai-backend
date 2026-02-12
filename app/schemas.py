from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---------------- BUYERS ----------------

class BuyerCreate(BaseModel):
    full_name: str
    email: str
    city: str
    state: Optional[str] = None
    asset_type: str
    min_budget: float
    max_budget: float


class BuyerOut(BaseModel):
    id: int
    full_name: str
    email: str
    city: str
    state: Optional[str]
    asset_type: str
    min_budget: float
    max_budget: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- DEALS ----------------

class DealCreate(BaseModel):
    title: str
    city: str
    state: Optional[str] = None
    asset_type: str
    price: float
    description: Optional[str] = None


class DealOut(BaseModel):
    id: int
    title: str
    city: str
    state: Optional[str]
    asset_type: str
    price: float
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- MATCHES ----------------

class MatchOut(BaseModel):
    id: int
    buyer_id: int
    deal_id: int
    created_at: datetime

    class Config:
        from_attributes = True
