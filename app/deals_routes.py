import uuid
from fastapi import APIRouter, HTTPException
from app.database import execute, fetch_all
from app.models import DealCreate, LearningEvent

from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import build_next_action
from app.ai_level5_learning import learn_adjustment

router = APIRouter(prefix="/deals", tags=["deals"])


# -------------------------
# LIST DEALS
# -------------------------
@router.get("")
def list_deals(limit: int = 50):
    rows = fetch_all(
        "SELECT * FROM deals ORDER BY created_at DESC LIMIT %s",
        (limit,)
    )
    return {"count": len(rows), "deals": rows}


# -------------------------
# CREATE DEAL (FIXED)
# -------------------------
@router.post("/create")
def create_deal(payload: DealCreate):
    try:
        deal_id = str(uuid.uuid4())
        deal = payload.model_dump()

        # --- AI PIPELINE ---
        scores = score_deal(deal)
        decision = decide_action(deal, scores)
        next_action = build_next_action(deal, decision)

        # --- DATABASE INSERT ---
        execute(
            """
            INSERT INTO deals (
                id,
                source,
                external_id,
                asset_type,
                title,
                description,
                location,
                url,
                price,
                currency,
                profit_score,
                urgency_score,
                risk_score,
                ai_score,
                decision,
                next_action,
                status
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s
            )
            """,
            (
                deal_id,
                deal.get("source"),
                deal.get("external_id"),
                deal.get("asset_type"),
                deal.get("title"),
                deal.get("description"),
                deal.get("location"),
                deal.get("url"),
                deal.get("price"),
                deal.get("currency"),
                scores.get("profit_score", 0),
                scores.get("urgency_score", 0),
                scores.get("risk_score", 0),
                scores.get("ai_score", 0),
                decision,
                str(next_action),
                "new"
            )
        )

        # --- LEARNING LOOP ---
        learn_adjustment(deal_id, decision, scores)

        return {
            "ok": True,
            "id": deal_id,
            "decision": decision,
            "scores": scores
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# LEARNING EVENT
# -------------------------
@router.post("/learn")
def learn(payload: LearningEvent):
    execute(
        """
        INSERT INTO learning_events (id, deal_id, event_type, metadata)
        VALUES (%s,%s,%s,%s)
        """,
        (
            str(uuid.uuid4()),
            payload.deal_id,
            payload.event_type,
            str(payload.metadata)
        )
    )
    return {"ok": True}
