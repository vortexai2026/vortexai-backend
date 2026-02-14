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


class BuyerOut(BaseModel):
    id: int
    full_name: str
    phone: str
    city: str
    budget_min: float
    budget_max: float
    asset_type: str

    class Config:
        from_attributes = True


# ---------------- DEALS ----------------
class DealCreate(BaseModel):
    title: str
    city: str
    asset_type: str
    price: float
    description: str


class DealOut(BaseModel):
    id: int
    title: str
    city: str
    asset_type: str
    price: float
    description: str
    matched_buyer_id: int | None

    class Config:
        from_attributes = True
