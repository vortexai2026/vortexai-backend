from pydantic import BaseModel, EmailStr
from typing import Optional

class BuyerCreateIn(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    tier: Optional[str] = "Weak Buyer"
    score: Optional[int] = 0
