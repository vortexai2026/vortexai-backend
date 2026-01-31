from pydantic import BaseModel, EmailStr
from typing import Optional

class DealCreate(BaseModel):
    title: str
    location: str
    price: float
    asset_type: str = "real_estate"
    source: str = "manual"
    url: Optional[str] = None
    market_value: Optional[float] = None
    motivation: Optional[str] = None
    days_on_market: Optional[int] = None

class CheckoutRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    location: Optional[str] = None
    asset_type: Optional[str] = None
    budget: Optional[str] = None
