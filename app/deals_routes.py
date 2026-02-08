import uuid
from fastapi import APIRouter
from app.database import execute, fetch_all, fetch_one
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
    deal_id = str(uuid.uuid4())
    deal = payload.model_dump()

    scores = score_deal(deal)
    decision = decide_action(deal, scores)
    next_action = build_next_action(deal, decision)

    execute("""
        INSERT INTO deals (
            id, source, external_id, asset_type, title, description, location, url, price, currency,
            profit_score, urgency_score, risk_score, ai_score, decision, next_action
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s::jsonb
        )
    """, (
        deal_id,
        deal["source"],
        deal.get("external_id"),
        deal["asset_type"],
        deal["title"],
        deal.get("description"),
        deal.get("location"),
        deal.get("url"),
        deal.get("price"),
        deal.get("currency"),
        scores["profit_score"],
        scores["urgency_score"],
        scores["risk_score"],
        scores["ai_score"],
        decision,
        str(next_action).replace("'", '"')
    ))

    learn_adjustment(deal_id, decision, scores)

    return {"id": deal_id, "decision": decision, "scores": scores}

@router.post("/learn")
def learn(payload: LearningEvent):
    execute("""
        INSERT INTO learning_events (id, deal_id, event_type, metadata)
        VALUES (%s,%s,%s,%s::jsonb)
    """, (
        str(uuid.uuid4()),
        payload.deal_id,
        payload.event_type,
        str(payload.metadata).replace("'", '"')
    ))
    return {"ok": True}
