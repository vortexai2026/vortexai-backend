# app/deals_routes.py

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.database import fetch_all, execute
from app.models import DealCreate

# AI LEVELS
from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import execute_action

router = APIRouter(prefix="/deals", tags=["deals"])


# =========================
# CREATE DEAL (POST)
# =========================
@router.post("/create")
def create_deal(payload: DealCreate):
    deal_id = str(uuid.uuid4())

    deal = {
        "id": deal_id,
        "title": payload.title,
        "price": payload.price,
        "location": payload.location,
        "asset_type": payload.asset_type,
        "description": payload.description,
    }

    # -------- LEVEL 2: SCORING --------
    scores = score_deal(deal)

    # -------- LEVEL 3: DECISION --------
    decision = decide_action(deal, scores)

    # -------- LEVEL 4: ACTION --------
    action_result = execute_action(deal, decision)

    try:
        execute(
            """
            INSERT INTO deals (
                id,
                title,
                price,
                location,
                asset_type,
                description,
                profit_score,
                urgency_score,
                risk_score,
                ai_score,
                decision,
                status,
                created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                deal_id,
                payload.title,
                payload.price,
                payload.location,
                payload.asset_type,
                payload.description,
                scores["profit_score"],
                scores["urgency_score"],
                scores["risk_score"],
                scores["ai_score"],
                decision,
                action_result["status"],
                datetime.utcnow(),
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "deal_id": deal_id,
        "scores": scores,
        "decision": decision,
        "action": action_result,
    }


# =========================
# LIST DEALS (GET)
# =========================
@router.get("")
def list_deals():
    return fetch_all(
        """
        SELECT
            id,
            title,
            price,
            location,
            asset_type,
            profit_score,
            urgency_score,
            risk_score,
            ai_score,
            decision,
            status,
            created_at
        FROM deals
        ORDER BY created_at DESC
        LIMIT 100
        """
    )
