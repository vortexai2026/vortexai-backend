import uuid
from fastapi import APIRouter, HTTPException

from app.database import execute, fetch_all, fetch_one
from app.matcher import match_buyers_for_deal

router = APIRouter(prefix="/deals", tags=["deals"])


# ===============================
# CREATE DEAL + AUTO-MATCH BUYERS
# ===============================
@router.post("/create")
def create_deal(payload: dict):
    deal_id = str(uuid.uuid4())

    try:
        # 1️⃣ Insert deal
        execute("""
            INSERT INTO deals (
                id,
                source,
                asset_type,
                title,
                description,
                location,
                price,
                currency,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
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

        # 2️⃣ Fetch deal back
        deal = fetch_one(
            "SELECT * FROM deals WHERE id = %s",
            (deal_id,)
        )

        if not deal:
            raise Exception("Deal insert failed")

        # 3️⃣ Auto-match buyers
        matches = match_buyers_for_deal(deal)

        # 4️⃣ Return result
        return {
            "ok": True,
            "deal_id": deal_id,
            "matched_buyers": len(matches)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"create_deal failed: {str(e)}"
        )


# ===============================
# LIST DEALS
# ===============================
@router.get("/")
def list_deals(limit: int = 50):
    deals = fetch_all("""
        SELECT *
        FROM deals
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    return {
        "count": len(deals),
        "deals": deals
    }


# ===============================
# GET SINGLE DEAL
# ===============================
@router.get("/{deal_id}")
def get_deal(deal_id: str):
    deal = fetch_one(
        "SELECT * FROM deals WHERE id = %s",
        (deal_id,)
    )

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return deal
