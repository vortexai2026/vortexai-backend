# deals_routes.py
from fastapi import APIRouter, HTTPException
from app.models import DealCreate, DealOut
from app.database import execute, fetch_all, fetch_one
import uuid

router = APIRouter(prefix="/deals", tags=["Deals"])

# Create a new deal
@router.post("/create")
def create_deal(payload: DealCreate):
    deal_id = str(uuid.uuid4())
    try:
        execute("""
            INSERT INTO deals (
                id, title, description, price, city, asset_type, active
            ) VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (
            deal_id,
            payload.title,
            payload.description,
            payload.price,
            payload.city,
            payload.asset_type.lower().strip()
        ))
        return {"ok": True, "deal_id": deal_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_deal failed: {str(e)}")

# List all active deals
@router.get("", response_model=list[DealOut])
def list_deals(limit: int = 50):
    deals = fetch_all("""
        SELECT * FROM deals
        WHERE active = TRUE
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    return deals

# Get a single deal by ID
@router.get("/{deal_id}", response_model=DealOut)
def get_deal(deal_id: str):
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

# Match buyers to a deal
@router.get("/match/{deal_id}")
def match_buyers(deal_id: str):
    # Example: find buyers interested in this asset type and city
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    buyers = fetch_all("""
        SELECT * FROM buyers
        WHERE active = TRUE
        AND (asset_type = %s OR asset_type = 'any')
        AND (city = %s OR city IS NULL)
        ORDER BY created_at DESC
    """, (deal["asset_type"], deal["city"]))

    return {"deal": deal, "matched_buyers_count": len(buyers), "buyers": buyers}
