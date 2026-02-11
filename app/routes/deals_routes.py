import uuid
from fastapi import APIRouter, HTTPException
from app.database import execute, fetch_all, fetch_one
from app.ai.ai_buyer_matcher import match_buyers_to_deal

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("/create")
def create_deal(payload: dict):
    deal_id = str(uuid.uuid4())

    try:
        execute("""
            INSERT INTO deals (
                id, title, description, location,
                price, asset_type, seller_name, seller_email
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            deal_id,
            payload.get("title"),
            payload.get("description"),
            payload.get("location"),
            payload.get("price"),
            payload.get("asset_type"),
            payload.get("seller_name"),
            payload.get("seller_email")
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create deal: {str(e)}")

    return {"ok": True, "deal_id": deal_id}


@router.get("")
def list_deals(limit: int = 50):
    deals = fetch_all("""
        SELECT * FROM deals
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    return {"count": len(deals), "deals": deals}


@router.get("/{deal_id}")
def get_deal(deal_id: str):
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.get("/match/{deal_id}")
def match_buyers(deal_id: str):
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    matches = match_buyers_to_deal(dict(deal))
    return {"deal_id": deal_id, "matches": matches}
