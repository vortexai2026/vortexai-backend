# app/routes/buyers.py
from fastapi import APIRouter
from app.db import database as db

router = APIRouter(tags=["Buyers"])

@router.post("/create")
async def create_buyer(name: str, email: str):
    query = "INSERT INTO buyers(name, email) VALUES($1, $2)"
    await db.execute(query, name, email)
    return {"ok": True, "message": "Buyer created"}

@router.get("/")
async def list_buyers():
    query = "SELECT * FROM buyers"
    buyers = await db.fetch_all(query)
    return {"ok": True, "buyers": buyers}

@router.get("/{buyer_id}")
async def get_buyer(buyer_id: int):
    query = "SELECT * FROM buyers WHERE id=$1"
    buyer = await db.fetch_one(query, buyer_id)
    return {"ok": True, "buyer": buyer}

@router.post("/disable/{buyer_id}")
async def disable_buyer(buyer_id: int):
    query = "UPDATE buyers SET active=false WHERE id=$1"
    await db.execute(query, buyer_id)
    return {"ok": True, "message": "Buyer disabled"}
