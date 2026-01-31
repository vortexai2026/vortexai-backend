from pydantic import BaseModel, EmailStr
from typing import Optional

class DealCreate(BaseModel):
    title: str
    price: float
    location: str
    asset_type: str
    source: str


class CheckoutRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    location: Optional[str] = None
    asset_type: Optional[str] = None
    budget: Optional[float] = None
