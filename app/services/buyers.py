# app/routes/buyers.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import db

router = APIRouter(prefix="/buyers", tags=["buyers"])

class BuyerCreate(BaseModel):
    name: str
    email: str
    asset_types: list[str]
    cities: list[str]
    min_price: float
    max_price: float
    tier: str = "free"

@router.post("/create")
def create_buyer(buyer: BuyerCreate):
    query = """
    INSERT INTO buyers
    (name, email, asset_types, cities, min_price, max_price, tier)
    VALUES
    (:name, :email, :asset_types, :cities, :min_price, :max_price, :tier)
    RETURNING id;
    """
    try:
        # Convert lists to JSON strings if your DB column type is JSON or TEXT
        data = buyer.dict()
        data["asset_types"] = str(data["asset_types"])
        data["cities"] = str(data["cities"])

        new_id = db.fetch_one(query, data)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_buyer failed: {str(e)}")
