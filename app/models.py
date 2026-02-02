from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class DealCreate(BaseModel):
    id: UUID
    title: str
    price: float = 0
    location: str = ""
    asset_type: str = ""
    source: str = ""

class CheckoutRequest(BaseModel):
    email: EmailStr
    name: str = ""
    location: str = ""
    asset_type: str = "real_estate"
    budget: float = 0

class OutcomeCreate(BaseModel):
    deal_id: UUID
    outcome: str = Field(..., description="sold|closed|profit|failed|scam|loss")
    notes: str = ""
