import uuid
from fastapi import APIRouter, HTTPException
from app.database import fetch_all, fetch_one, execute
from app.models import DealCreate, OutcomeCreate

from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import build_next_action
from app.ai_level5_learning import learn_adjustment

router = APIRouter(prefix="/deals", tags=["deals"])

@router.get("")
def list_deals():
    return {"count": len(fetch_all("SELECT * FROM deals ORDER BY created_at DESC LIMIT 200")), "deals": fetch_all("SELECT * FROM deals ORDER BY created_at DESC LIMIT 200")}

@router.post("/create")
def create_deal(deal: DealCreate):
    # Save first
    execute("""
        INSERT INTO deals (id, title, price, location, asset_type, source, status)
        VALUES (%s,%s,%s,%s,%s,%s,'new')
        ON CONFLICT (id) DO NOTHING
    """, (str(deal.id), deal.title, deal.price, deal.location, deal.asset_type, deal.source))

    # Pull it back as dict for scoring
    row = fetch_one("SELECT * FROM deals WHERE id=%s", (str(deal.id),))
    if not row:
        raise HTTPException(status_code=500, detail="Deal insert failed")

    deal_dict = dict(row)

    # ✅ Level 2 → 3 → 4 on create (auto)
    scores = score_deal(deal_dict)
    decision = decide_action(scores, deal_dict)
    next_action = build_next_action(decision, deal_dict)

    execute("""
        UPDATE deals
        SET profit_score=%s,
            urgency_score=%s,
            risk_score=%s,
            ai_score=%s,
            decision=%s,
            next_action=%s,
            status=%s
        WHERE id=%s
    """, (
        scores["profit_score"],
        scores["urgency_score"],
        scores["risk_score"],
        scores["ai_score"],
        decision,
        next_action,
        "processed",
        str(deal.id)
    ))

    return {
        "status": "ok",
        "id": str(deal.id),
        "scores": scores,
        "decision": decision,
        "next_action": next_action
    }

@router.post("/outcome")
def record_outcome(payload: OutcomeCreate):
    adj = learn_adjustment(payload.outcome)
    outcome_id = str(uuid.uuid4())

    execute("""
        INSERT INTO outcomes (id, deal_id, outcome, notes)
        VALUES (%s,%s,%s,%s)
    """, (outcome_id, str(payload.deal_id), payload.outcome, payload.notes))

    # Optional: shift ai_score slightly to simulate learning
    deal = fetch_one("SELECT ai_score FROM deals WHERE id=%s", (str(payload.deal_id),))
    if deal:
        new_score = float(deal["ai_score"] or 0) * (1 + adj)
        execute("UPDATE deals SET ai_score=%s WHERE id=%s", (new_score, str(payload.deal_id)))

    return {"status": "ok", "outcome_id": outcome_id, "adjustment": adj}
