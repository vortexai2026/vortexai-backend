from pydantic import BaseModel
from typing import Optional, Dict, Any


class DealCreate(BaseModel):
    source: str
    external_id: Optional[str] = None
    asset_type: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "USD"


class LearningEvent(BaseModel):
    deal_id: str
    event_type: str
    metadata: Optional[Dict[str, Any]] = None


class BuyerCreate(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None

    asset_type: str
    city: Optional[str] = None
    min_price: Optional[float] = 0
    max_price: Optional[float] = 999999999

    tier: Optional[str] = "free"
