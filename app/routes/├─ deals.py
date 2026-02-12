# deals_routes.py
from fastapi import APIRouter, HTTPException
from app.models import DealCreate
from app.database import execute, fetch_all, fetch_one

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.post("/create")
def create_deal(payload: DealCreate):
    """
    Create a new deal
    """
    import uuid
    deal_id = str(uuid.uuid4())

    try:
        execute("""
            INSERT INTO deals (
                id, title, description, price, city, asset_type, active
            ) VALUES (%s,%s,%s,%s,%s,%s,TRUE)
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


@router.get("")
def list_deals(limit: int = 50):
    """
    List all active deals (default limit 50)
    """
    deals = fetch_all("""
        SELECT * FROM deals
        WHERE active = TRUE
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    return {"count": len(deals), "deals": deals}


@router.get("/{deal_id}")
def get_deal(deal_id: str):
    """
    Get a single deal by ID
    """
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.get("/match/{deal_id}")
def match_buyers(deal_id: str):
    """
    Find buyers that match this deal
    """
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    buyers = fetch_all("""
        SELECT * FROM buyers
        WHERE active=TRUE
        AND (asset_type=%s OR asset_type='any')
        AND min_price <= %s
        AND max_price >= %s
    """, (deal["asset_type"], deal["price"], deal["price"]))

    return {"deal_id": deal_id, "matches": buyers, "count": len(buyers)}
