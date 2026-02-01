# app/ai_level5_learning.py

from typing import Dict
from app.database import execute, fetch_all

"""
LEVEL 5: Learning AI
This module updates internal weights based on real outcomes.
No OpenAI needed. 100% deterministic and safe.
"""


# -----------------------------
# Learning rules
# -----------------------------
LEARNING_RULES = {
    "sold": 0.15,
    "closed": 0.15,
    "profit": 0.15,
    "failed": -0.15,
    "scam": -0.25,
    "expired": -0.10,
}


def learn_adjustment(outcome: str) -> float:
    """
    Converts an outcome into a learning adjustment.
    """
    if not outcome:
        return 0.0
    return LEARNING_RULES.get(outcome.lower(), 0.0)


# -----------------------------
# Apply learning to scores
# -----------------------------
def apply_learning(deal_id: str, outcome: str):
    """
    Adjust AI scores after we know the outcome.
    """

    adjustment = learn_adjustment(outcome)

    # Update deal scores slightly
    execute(
        """
        UPDATE deals
        SET
            ai_score = LEAST(100, GREATEST(0, ai_score + (%s * 100))),
            learning_outcome = %s,
            learned_at = NOW()
        WHERE id = %s
        """,
        (adjustment, outcome, deal_id),
    )

    # Log learning history
    execute(
        """
        INSERT INTO ai_learning_log (
            deal_id,
            outcome,
            adjustment,
            created_at
        )
        VALUES (%s,%s,%s,NOW())
        """,
        (deal_id, outcome, adjustment),
    )

    return {
        "deal_id": deal_id,
        "outcome": outcome,
        "adjustment": adjustment,
        "status": "learning_applied",
    }


# -----------------------------
# Auto-learn from finished deals
# -----------------------------
def run_learning_cycle():
    """
    Finds completed deals and applies learning automatically.
    """

    deals = fetch_all(
        """
        SELECT id, status
        FROM deals
        WHERE status IN ('sold','failed','scam','expired')
        AND learned_at IS NULL
        LIMIT 50
        """
    )

    results = []

    for d in deals:
        result = apply_learning(d["id"], d["status"])
        results.append(result)

    return {
        "processed": len(results),
        "results": results,
    }

