# app/deals_routes.py
import uuid
from fastapi import APIRouter, HTTPException
from app.database import execute, fetch_all, fetch_one
from app.models import DealCreate, LearningEvent
from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import build_next_action
from app.ai_level5_learning import learn_adjustment

router = APIRouter(prefix="/deals", tags=["deals"])

@router.get("")
def list_deals(limit: int = 50):
    rows = fetch_all("""
        SELECT * FROM deals
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    return {"count": len(rows), "deals": rows}

@router.post("/create")
def create_deal(payload: DealCreate):
    try:
        deal_id = str(uuid.uuid4())
        deal = payload.model_dump()

        # 1) Score
        scores = score_deal(deal)

        # 2) Decide
        decision = decide_action(deal, scores)

        # 3) Action
        next_action = build_next_action(deal, decision)

        # 4) Insert (upsert by source+external_id if provided)
        if deal.get("external_id"):
            existing = fetch_one(
                "SELECT id FROM deals WHERE source=%s AND external_id=%s LIMIT 1",
                (deal["source"], deal["external_id"])
            )
            if existing:
                deal_id = str(existing["id"])
                execute("""
                    UPDATE deals SET
                      asset_type=%s, title=%s, description=%s, location=%s, url=%s, price=%s, currency=%s,
                      profit_score=%s, urgency_score=%s, risk_score=%s, ai_score=%s,
                      decision=%s, next_action=%s::jsonb
                    WHERE id=%s
                """, (
                    deal["asset_type"], deal["title"], deal.get("description",""), deal.get("location",""),
                    deal.get("url",""), deal.get("price",0), deal.get("currency","USD"),
                    scores["profit_score"], scores["urgency_score"], scores["risk_score"], scores["ai_score"],
                    decision, str(next_action).replace("'", '"'),
                    deal_id
                ))
                learn_adjustment(deal_id, decision, scores)
                return {"ok": True, "id": deal_id, "decision": decision, "scores": scores, "next_action": next_action}

        execute("""
            INSERT INTO deals (
              id, source, external_id, asset_type, title, description, location, url, price, currency,
              profit_score, urgency_score, risk_score, ai_score,
              decision, next_action
            ) VALUES (
              %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
              %s,%s,%s,%s,
              %s,%s::jsonb
            )
        """, (
            deal_id, deal["source"], deal.get("external_id"),
            deal["asset_type"], deal["title"], deal.get("description",""),
            deal.get("location",""), deal.get("url",""),
            deal.get("price",0), deal.get("currency","USD"),
            scores["profit_score"], scores["urgency_score"], scores["risk_score"], scores["ai_score"],
            decision, str(next_action).replace("'", '"')
        ))

        # 5) Learning log
        learn_adjustment(deal_id, decision, scores)

        return {"ok": True, "id": deal_id, "decision": decision, "scores": scores, "next_action": next_action}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learn")
def add_learning_event(payload: LearningEvent):
    execute("""
        INSERT INTO learning_events (id, deal_id, event_type, metadata)
        VALUES (%s, %s, %s, %s::jsonb)
    """, (str(uuid.uuid4()), payload.deal_id, payload.event_type, str(payload.metadata).replace("'", '"')))
    return {"ok": True}
