# app/schemas/buyer_import.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class BuyerImport(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    market_tag: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    buy_box_beds: Optional[int] = None
    buy_box_baths: Optional[float] = None

    proof_of_funds: Optional[str] = None
    notes: Optional[str] = None

    tier: Optional[str] = "free"
    status: Optional[str] = "active"
