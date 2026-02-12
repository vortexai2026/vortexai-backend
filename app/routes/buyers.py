from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["buyers"])

class BuyerCreate(BaseModel):
    name: str
    email: str
    asset_type: str
    city: str
    min_price: float
    max_price: float
    tier: str = "free"

@router.post("/create")
def create_buyer(buyer: BuyerCreate):
    return {"message": "Buyer created", "buyer": buyer.dict()}

@router.get("/")
def list_buyers():
    return {"buyers": []}

@router.get("/{buyer_id}")
def get_buyer(buyer_id: int):
    return {"buyer_id": buyer_id, "name": "Test Buyer"}

@router.post("/disable/{buyer_id}")
def disable_buyer(buyer_id: int):
    return {"buyer_id": buyer_id, "status": "disabled"}
