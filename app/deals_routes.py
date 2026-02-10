import uuid
import json
from fastapi import APIRouter, HTTPException
from app.database import execute, fetch_all, fetch_one
from app.models import DealCreate, LearningEvent

from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import build_next_action
from app.ai_level5_learning import learn_adjustment
from app.ai_outreach_writer import build_outreach_message

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
        next_action_json = json.dumps(next_action, default=str)

        # Upsert if external_id exists
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
                    deal.get("url",""), deal.get("price"), deal.get("currency","USD"),
                    scores["profit_score"], scores["urgency_score"], scores["risk_score"], scores["ai_score"],
                    decision, next_action_json, deal_id
                ))

                learn_adjustment(deal_id, decision, scores)

                if decision in ("contact_seller", "review"):
                    draft = build_outreach_message(deal, decision)
                    execute("""
                        INSERT INTO outreach_messages (id, deal_id, channel, target, subject, body, status)
                        VALUES (%s,%s,'manual',NULL,%s,%s,'draft')
                    """, (str(uuid.uuid4()), deal_id, draft["subject"], draft["body"]))

                return {"ok": True, "id": deal_id, "decision": decision, "scores": scores, "next_action": next_action}

        # Insert new deal
        execute("""
            INSERT INTO deals (
                id, source, external_id, asset_type, title, description, location, url, price, currency,
                profit_score, urgency_score, risk_score, ai_score, decision, next_action, status
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s::jsonb,%s
            )
        """, (
            deal_id,
            deal["source"],
            deal.get("external_id"),
            deal["asset_type"],
            deal["title"],
            deal.get("description",""),
            deal.get("location",""),
            deal.get("url",""),
            deal.get("price"),
            deal.get("currency","USD"),
            scores.get("profit_score", 0),
            scores.get("urgency_score", 0),
            scores.get("risk_score", 0),
            scores.get("ai_score", 0),
            decision,
            next_action_json,
            "new"
        ))

        learn_adjustment(deal_id, decision, scores)

        if decision in ("contact_seller", "review"):
            draft = build_outreach_message(deal, decision)
            execute("""
                INSERT INTO outreach_messages (id, deal_id, channel, target, subject, body, status)
                VALUES (%s,%s,'manual',NULL,%s,%s,'draft')
            """, (str(uuid.uuid4()), deal_id, draft["subject"], draft["body"]))

        return {"ok": True, "id": deal_id, "decision": decision, "scores": scores, "next_action": next_action}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create deal failed: {str(e)}")

@router.post("/learn")
def learn(payload: LearningEvent):
    try:
        execute("""
            INSERT INTO learning_events (id, deal_id, event_type, metadata)
            VALUES (%s,%s,%s,%s::jsonb)
        """, (str(uuid.uuid4()), payload.deal_id, payload.event_type, json.dumps(payload.metadata or {})))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learn failed: {str(e)}")
