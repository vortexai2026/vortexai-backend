import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException
from app.database import fetch_all, fetch_one, execute
from app.models import DealCreate

# AI PIPELINE
from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level6_strategy import apply_strategy
from app.ai_level4_action import take_action

router = APIRouter(prefix="/deals", tags=["deals"])


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# =========================
# CREATE DEAL (FULL AI PIPELINE)
# =========================
@router.post("/create")
def create_deal(payload: DealCreate):
    """
    FLOW:
    1) Save deal to DB
    2) Level 2 → score deal
    3) Level 6 → apply learning strategy
    4) Level 3 → decide action
    5) Level 4 → execute action
    """

    deal_id = str(uuid.uuid4())

    deal_dict = {
        "id": deal_id,
        "title": payload.title,
        "price": payload.price,
        "location": payload.location,
        "asset_type": payload.asset_type,
        "description": payload.description,
        "source": payload.source,
    }

    # 1️⃣ INSERT DEAL
    execute(
        """
        INSERT INTO deals (
            id, title, price, location, asset_type,
            description, source, status, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            deal_id,
            payload.title,
            payload.price,
            payload.location,
            payload.asset_type,
            payload.description,
            payload.source,
            "new",
            _utc_now(),
        ),
    )

    # 2️⃣ LEVEL 2 — SCORING
    raw_scores = score_deal(deal_dict)

    # 3️⃣ LEVEL 6 — STRATEGY (learning applied)
    scores = apply_strategy(raw_scores)

    # 4️⃣ LEVEL 3 — DECISION
    decision = decide_action(deal_dict, scores)

    # 5️⃣ LEVEL 4 — ACTION
    action_result = take_action(deal_dict, scores, decision)

    return {
        "ok": True,
        "deal_id": deal_id,
        "scores": scores,
        "decision": decision,
        "action": action_result,
    }


# =========================
# LIST DEALS
# =========================
@router.get("")
def list_deals(limit: int = 50):
    rows = fetch_all(
        """
        SELECT *
        FROM deals
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (limit,),
    )
    return {"count": len(rows), "deals": rows}
