from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class DealCreate(BaseModel):
    title: str
    price: Optional[float] = None
    location: Optional[str] = None
    asset_type: Optional[str] = Field(default="real_estate")
    source: Optional[str] = Field(default="manual")
    status: Optional[str] = Field(default="new")

class CheckoutRequest(BaseModel):
    email: EmailStr
    name: str = ""
    location: str = ""
    asset_type: str = "real_estate"
    budget: float = 0
