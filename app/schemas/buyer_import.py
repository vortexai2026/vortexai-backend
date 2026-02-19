from pydantic import BaseModel
from typing import Optional

class BuyerImport(BaseModel):
    name: str
    email: str
    phone: str
    city: str
    max_price: float
    preferred_zip: str
    rehab_tolerance: str
    buy_box_notes: Optional[str] = None
