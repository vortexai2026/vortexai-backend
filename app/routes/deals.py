# app/routes/deals.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import database as db
from app.worker.match_buyers import match_buyers_for_deal  # import the matcher

router = APIRouter(tags=["deals"])

# Pydantic model
class DealCreate(BaseModel):
    title: str
    asset_type: str
    city: str
    price: float
    description: str = ""

@router.post("/deals/create")
def create_deal(deal: DealCreate):
    query = """
    INSERT INTO deals (title, asset_type, city, price, description)
    VALUES (:title, :asset_type, :city, :price, :description)
    RETURNING id;
    """
    try:
        new_id = db.fetch_one(query, deal.dict())["id"]
        
        # 🔹 Trigger Matching Engine right after creating the deal
        match_buyers_for_deal(new_id)
        
        return {"id": new_id, "message": "Deal created and matched successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_deal failed: {str(e)}")
