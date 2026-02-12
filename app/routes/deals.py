# app/routes/deals.py
from fastapi import APIRouter
from app.db import database as db

router = APIRouter(tags=["Deals"])

@router.post("/deals/create")
async def create_deal(title: str, value: float):
    query = "INSERT INTO deals(title, value) VALUES($1, $2)"
    await db.execute(query, title, value)
    return {"ok": True, "message": "Deal created"}

@router.get("/deals")
async def list_deals():
    query = "SELECT * FROM deals"
    deals = await db.fetch_all(query)
    return {"ok": True, "deals": deals}

@router.get("/deals/{deal_id}")
async def get_deal(deal_id: int):
    query = "SELECT * FROM deals WHERE id=$1"
    deal = await db.fetch_one(query, deal_id)
    return {"ok": True, "deal": deal}

@router.get("/deals/match/{deal_id}")
async def match_buyers(deal_id: int):
    # Placeholder matching logic
    query = "SELECT * FROM buyers WHERE active=true"
    buyers = await db.fetch_all(query)
    return {"ok": True, "matched_buyers": buyers}
