# app/routes/deals.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.db import database as db
from app.worker.match_buyers import match_buyers_for_deal

router = APIRouter(tags=["deals"])

# Pydantic model for creating a deal
class DealCreate(BaseModel):
    title: str
    asset_type: str
    city: str
    price: float
    description: str = ""

# Create a new deal and optionally run matching in background
@router.post("/deals/create")
def create_deal(deal: DealCreate, background_tasks: BackgroundTasks):
    query = """
    INSERT INTO deals (title, asset_type, city, price, description)
    VALUES (:title, :asset_type, :city, :price, :description)
    RETURNING id;
    """
    try:
        new_id = db.fetch_one(query, deal.dict())["id"]

        # Run matching in background
        background_tasks.add_task(match_buyers_for_deal, new_id)

        return {"id": new_id, "message": "Deal created and matching started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_deal failed: {str(e)}")

# List all deals
@router.get("/deals")
def list_deals():
    query = "SELECT * FROM deals;"
    return db.fetch_all(query)

# Get a single deal by ID
@router.get("/deals/{deal_id}")
def get_deal(deal_id: int):
    query = "SELECT * FROM deals WHERE id = :id;"
    deal = db.fetch_one(query, {"id": deal_id})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

# Match buyers for a specific deal manually
@router.get("/deals/match/{deal_id}")
def match_buyers_endpoint(deal_id: int):
    matched_buyers = match_buyers_for_deal(deal_id)
    if not matched_buyers:
        raise HTTPException(status_code=404, detail="No buyers matched for this deal")
    return {"deal_id": deal_id, "matched_buyers": matched_buyers}
