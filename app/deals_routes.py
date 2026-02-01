import uuid
from fastapi import APIRouter, HTTPException
from app.database import fetch_all, fetch_one, execute
from app.models import DealCreate
from app.ai_level2_scoring import score_deal

router = APIRouter(prefix="/deals", tags=["deals"])

@router.post("/create")
def create_deal(payload: DealCreate):
    deal_id = str(uuid.uuid4())

    # Build deal dict for scoring
    deal_dict = payload.model_dump()
    deal_dict["id"] = deal_id

    scores = score_deal(deal_dict)

    execute("""
        INSERT INTO deals (id, title, price, location, asset_type, source, status, ai_score, profit_score, urgency_score, risk_score)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        deal_id,
        payload.title,
        payload.price,
        payload.location,
        payload.asset_type,
        payload.source,
        payload.status,
        scores["ai_score"],
        scores["profit_score"],
        scores["urgency_score"],
        scores["risk_score"]
    ))

    return {"status": "created", "id": deal_id, "scores": scores}

@router.get("")
def list_deals():
    return fetch_all("SELECT * FROM deals ORDER BY created_at DESC LIMIT 100")

@router.get("/{deal_id}")
def get_deal(deal_id: str):
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal
