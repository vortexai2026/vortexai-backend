from pydantic import BaseModel

# ---------------- USERS ----------------
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ---------------- BUYERS ----------------
class BuyerCreate(BaseModel):
    full_name: str
    phone: str
    city: str
    budget_min: float
    budget_max: float
    asset_type: str

class BuyerOut(BuyerCreate):
    id: int
    class Config:
        orm_mode = True

# ---------------- DEALS ----------------
class DealCreate(BaseModel):
    title: str
    city: str
    asset_type: str
    price: float
    description: str

class DealOut(DealCreate):
    id: int
    matched_buyer_id: int | None = None
    class Config:
        orm_mode = True

# ---------------- MATCHES ----------------
class MatchOut(BaseModel):
    deal_id: int
    buyer_id: int
    class Config:
        orm_mode = True
