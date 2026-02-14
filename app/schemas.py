from pydantic import BaseModel, Field, validator
from typing import Optional


# =========================
# BUYER
# =========================

class BuyerCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2)
    budget_min: float = Field(..., gt=0)
    budget_max: float = Field(..., gt=0)
    asset_type: str = Field(..., min_length=2)

    @validator("budget_max")
    def validate_budget(cls, v, values):
        if "budget_min" in values and v < values["budget_min"]:
            raise ValueError("budget_max must be greater than or equal to budget_min")
        return v


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


# =========================
# DEAL
# =========================

class DealCreate(BaseModel):
    title: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    asset_type: str = Field(..., min_length=2)
    price: float = Field(..., gt=0)
    description: str = Field(..., min_length=5)


class DealOut(BaseModel):
    id: int
    title: str
    city: str
    asset_type: str
    price: float
    description: str
    matched_buyer_id: Optional[int]

    class Config:
        from_attributes = True
