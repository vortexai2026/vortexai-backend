# app/deals_routes.py
import uuid
import json
from fastapi import APIRouter, HTTPException
from app.database import execute, fetch_all
from app.models import DealCreate, LearningEvent

from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import build_next_action
from app.ai_level5_learning import learn_adjustment

router = APIRouter(prefix="/deals", tags=["deals"])

@router.get("")
def list_deals(limit: int = 50):
    rows = fetch_all("SELECT * FROM deals ORDER BY created_at DESC LIMIT %s", (limit,))
    return {"count": len(rows), "deals": rows}

@router.post("/create")
def create_deal(payload: DealCreate):
    try:
        deal_id = str(uuid.uuid4())
        deal = payload.model_dump()

        scores = score_deal(deal)
        decision = decide_action(deal, scores)
        next_action = build_next_action(deal, decision)

        # ✅ ensure JSON serializable
        next_action_json = json.dumps(next_action, default=str)

        execute(
            """
            INSERT INTO deals (
                id, source, external_id, asset_type, title, description, location, url, price, currency,
                profit_score, urgency_score, risk_score, ai_score, decision, next_action, status
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s::jsonb,%s
            )
            """,
            (
                deal_id,
                deal["source"],                 # NOT NULL in DB
                deal.get("external_id"),
                deal["asset_type"],
                deal["title"],
                deal.get("description"),
                deal.get("location"),
                deal.get("url"),
                deal.get("price"),
                deal.get("currency", "USD"),
                scores.get("profit_score", 0),
                scores.get("urgency_score", 0),
                scores.get("risk_score", 0),
                scores.get("ai_score", 0),
                decision,
                next_action_json,               # ✅ cast to jsonb in SQL
                "new"
            )
        )

        learn_adjustment(deal_id, decision, scores)

        return {"ok": True, "id": deal_id, "decision": decision, "scores": scores}

    except Exception as e:
        # ✅ this makes Railway logs show the real DB error
        raise HTTPException(status_code=500, detail=f"Create deal failed: {str(e)}")

@router.post("/learn")
def learn(payload: LearningEvent):
    try:
        execute(
            """
            INSERT INTO learning_events (id, deal_id, event_type, metadata)
            VALUES (%s,%s,%s,%s::jsonb)
            """,
            (
                str(uuid.uuid4()),
                payload.deal_id,
                payload.event_type,
                json.dumps(payload.metadata or {})
            )
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learn failed: {str(e)}")
