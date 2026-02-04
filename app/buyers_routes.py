# app/buyers_routes.py
import uuid
from fastapi import APIRouter
from app.database import execute, fetch_all
from app.models import BuyerCreate

router = APIRouter(prefix="/buyers", tags=["buyers"])

@router.post("/apply")
def apply_buyer(payload: BuyerCreate):
    buyer_id = str(uuid.uuid4())
    execute("""
        INSERT INTO buyers (
            id, email, name, phone, location,
            asset_types, min_price, max_price,
            tier, plan
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (email) DO NOTHING
    """, (
        buyer_id,
        payload.email,
        payload.name,
        payload.phone,
        payload.location,
        payload.asset_types,
        payload.min_price,
        payload.max_price,
        payload.tier,
        payload.plan
    ))
    return {"ok": True, "buyer_id": buyer_id}

@router.get("")
def list_buyers():
    buyers = fetch_all("SELECT * FROM buyers ORDER BY created_at DESC")
    return {"count": len(buyers), "buyers": buyers}
