from typing import Optional, Literal
from pydantic import BaseModel, Field
from uuid import UUID

CarStatus = Literal["available", "reserved", "sold"]
LeadStatus = Literal["new", "contacted", "appointment", "closed"]

class CarCreate(BaseModel):
    stock_number: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    km: Optional[int] = None
    engine: Optional[str] = None
    transmission: Optional[str] = None
    features: Optional[str] = None
    cost: Optional[float] = None
    asking_price: Optional[float] = None
    status: CarStatus = "available"

class CarOut(CarCreate):
    id: UUID

class LeadCreate(BaseModel):
    car_id: Optional[UUID] = None
    lead_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = "facebook"
    message: Optional[str] = None
    status: LeadStatus = "new"

class LeadOut(LeadCreate):
    id: UUID

class MessageCreate(BaseModel):
    lead_id: UUID
    direction: Literal["inbound", "outbound"]
    message: str = Field(min_length=1)

class SaleCreate(BaseModel):
    car_id: UUID
    sold_price: Optional[float] = None
    profit: Optional[float] = None
    commission: Optional[float] = None
