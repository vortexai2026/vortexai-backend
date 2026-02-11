import uuid
from fastapi import APIRouter, HTTPException
from app.database import execute, fetch_all, fetch_one
from app.models import BuyerCreate

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.post("/create")
def create_buyer(payload: BuyerCreate):
    buyer_id = str(uuid.uuid4())
    try:
        execute("""
            INSERT INTO buyers (
                id, email, name, phone,
                asset_type, city, min_price, max_price,
                tier, active
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)
        """, (
            buyer_id,
            payload.email.lower().strip(),
            payload.name,
            payload.phone,
            payload.asset_type.lower().strip(),
            (payload.city or None),
            payload.min_price or 0,
            payload.max_price or 999999999,
            (payload.tier or "free").lower().strip()
        ))

        return {"ok": True, "buyer_id": buyer_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_buyer failed: {str(e)}")


@router.get("")
def list_buyers(limit: int = 50):
    buyers = fetch_all("""
        SELECT * FROM buyers
        WHERE active = TRUE
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    return {"count": len(buyers), "buyers": buyers}


@router.get("/{buyer_id}")
def get_buyer(buyer_id: str):
    buyer = fetch_one("SELECT * FROM buyers WHERE id=%s", (buyer_id,))
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return buyer


@router.post("/disable/{buyer_id}")
def disable_buyer(buyer_id: str):
    execute("UPDATE buyers SET active=FALSE WHERE id=%s", (buyer_id,))
    return {"ok": True, "buyer_id": buyer_id, "active": False}
