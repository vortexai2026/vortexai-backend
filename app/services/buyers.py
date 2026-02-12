# app/routes/buyers.py
from fastapi import APIRouter
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
    (name,email,phone,asset_types,cities,min_price,max_price,tier)
    VALUES
    (:name,:email,:phone,:asset_types,:cities,:min_price,:max_price,:tier)
    RETURNING id;
    """
    return db.fetch_one(query, buyer.dict())
