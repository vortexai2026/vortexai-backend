from pydantic import BaseModel
from typing import Optional, Dict, Any

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

class LearningEvent(BaseModel):
    deal_id: str
    event_type: str
    metadata: Dict[str, Any] = {}
