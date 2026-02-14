from pydantic import BaseModel, Field, ConfigDict

# ---------- USERS ----------
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


# ---------- BUYERS ----------
class BuyerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    phone: str = Field(min_length=5, max_length=50)
    city: str = Field(min_length=2, max_length=120)
    budget_min: float = Field(ge=0)
    budget_max: float = Field(ge=0)
    asset_type: str = Field(min_length=2, max_length=80)

class BuyerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    phone: str
    city: str
    budget_min: float
    budget_max: float
    asset_type: str
    owner_id: int | None = None


# ---------- DEALS ----------
class DealCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    city: str = Field(min_length=2, max_length=120)
    asset_type: str = Field(min_length=2, max_length=80)
    price: float = Field(gt=0)
    description: str = Field(min_length=5)

class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    city: str
    asset_type: str
    price: float
    description: str
    matched_buyer_id: int | None = None
