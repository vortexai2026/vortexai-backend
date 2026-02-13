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


# ---------------- DEALS ----------------

class DealCreate(BaseModel):
    title: str
    city: str
    asset_type: str
    price: float
    description: str
