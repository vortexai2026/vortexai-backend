import uuid
from fastapi import APIRouter
from app.database import fetch_all, execute
from app.models import DealCreate

router = APIRouter(prefix="/deals", tags=["deals"])

@router.post("/create")
def create_deal(deal: DealCreate):
    deal_id = str(uuid.uuid4())

    execute("""
        INSERT INTO deals (id, title, price, location, asset_type)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        deal_id,
        deal.title,
        deal.price,
        deal.location,
        deal.asset_type
    ))

    return {"status": "created", "deal_id": deal_id}

@router.get("")
def list_deals():
    return fetch_all("SELECT * FROM deals ORDER BY created_at DESC")
