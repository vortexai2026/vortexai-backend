from pydantic import BaseModel
from typing import Optional

class BuyerImport(BaseModel):
    email: str
    name: str
    asset_type: str
    city: str
    max_budget: float
    preferred_zip: Optional[str] = None
    rehab_tolerance: Optional[str] = None  # light / medium / heavy
    buy_box_notes: Optional[str] = None
    phone: Optional[str] = None
