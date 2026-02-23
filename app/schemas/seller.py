from pydantic import BaseModel, EmailStr
from typing import Optional

class SellerIntakeIn(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    property_address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    asking_price: Optional[float] = None
    reason: Optional[str] = None
    condition_notes: Optional[str] = None
