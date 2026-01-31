import uuid
from fastapi import APIRouter, HTTPException
from app.database import fetch_all, fetch_one, execute
from app.models import DealCreate

router = APIRouter(prefix="/deals", tags=["deals"])

@router.post("/create")
def create_deal(payload: DealCreate):
    deal_id = str(uuid.uuid4())
    execute("""
        INSERT INTO deals (id, title, location, price, asset_type, source, url, market_value, motivation, days_on_market)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        deal_id,
        payload.title,
        payload.location,
        payload.price,
        payload.asset_type,
        payload.source,
        payload.url,
        payload.market_value,
        payload.motivation,
        payload.days_on_market
    ))
    return {"status": "created", "deal_id": deal_id}

@router.get("")
def list_deals(limit: int = 50):
    rows = fetch_all("SELECT * FROM deals ORDER BY created_at DESC LIMIT %s", (limit,))
    return {"count": len(rows), "deals": rows}

@router.get("/{deal_id}")
def get_deal(deal_id: str):
    row = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Deal not found")
    return row
