import uuid
from fastapi import APIRouter, HTTPException
from app.database import execute, fetch_all, fetch_one

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("/create")
def create_deal(payload: dict):
    deal_id = str(uuid.uuid4())
    try:
        execute("""
            INSERT INTO deals (
                id, source, asset_type, title,
                description, location, price, currency, status
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            deal_id,
            payload["source"],
            payload["asset_type"].lower(),
            payload["title"],
            payload.get("description"),
            payload.get("location"),
            payload.get("price"),
            payload.get("currency", "USD"),
            "new"
        ))

        return {"ok": True, "deal_id": deal_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_deal failed: {str(e)}")


@router.get("/")
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
