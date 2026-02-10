from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class DealCreate(BaseModel):
    source: str
    external_id: Optional[str] = None
    asset_type: str
    title: str
    description: Optional[str] = ""
    location: Optional[str] = ""
    url: Optional[str] = ""
    price: Optional[float] = None
    currency: Optional[str] = "USD"

class LearningEvent(BaseModel):
    deal_id: str
    event_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BuyerCreate(BaseModel):
    email: str
    name: Optional[str] = ""
    phone: Optional[str] = ""
    location: Optional[str] = ""
    asset_types: List[str] = Field(default_factory=list)
    min_price: float = 0
    max_price: float = 999999999
    tier: str = "free"
    plan: str = "free"
