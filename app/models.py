# app/models.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List

class DealCreate(BaseModel):
    source: str
    external_id: Optional[str] = None
    asset_type: str
    title: str
    description: Optional[str] = ""
    location: Optional[str] = ""
    url: Optional[str] = ""
    price: Optional[float] = 0
    currency: Optional[str] = "USD"

class BuyerCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = ""
    phone: Optional[str] = ""
    location: Optional[str] = ""
    asset_types: List[str] = []
    min_price: float = 0
    max_price: float = 999999999
    tier: str = "free"
    plan: str = "free"

class CheckoutRequest(BaseModel):
    email: EmailStr
    name: str = ""
    location: str = ""
    asset_type: str = ""
    budget: float = 0

class LearningEvent(BaseModel):
    deal_id: str
    event_type: str
    metadata: Dict[str, Any] = {}
