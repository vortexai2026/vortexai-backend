from typing import Dict, Any
from app.database import fetch_one


def get_global_weight() -> float:
    row = fetch_one("SELECT weight FROM learning_weights LIMIT 1", ())
    if not row:
        return 1.0
    try:
        return float(row.get("weight") or 1.0)
    except Exception:
        return 1.0


def apply_strategy(scores: Dict[str, float]) -> Dict[str, float]:
    """
    LEVEL 6 – STRATEGY AI

    Purpose:
    - Adjust AI score slightly using learning weight
    - Example: if learning says "we are doing well", weight up a bit
    - if learning says "bad outcomes", weight down a bit
    """

    weight = get_global_weight()

    ai_score = float(scores.get("ai_score", 0))
    profit = float(scores.get("profit_score", 0))
    urgency = float(scores.get("urgency_score", 0))
    risk = float(scores.get("risk_score", 0))

    # apply small multiplier to ai_score only
    adjusted_ai = ai_score * weight

    # clamp
    adjusted_ai = max(0.0, min(100.0, adjusted_ai))

    return {
        "profit_score": round(profit, 2),
        "urgency_score": round(urgency, 2),
        "risk_score": round(risk, 2),
        "ai_score": round(adjusted_ai, 2),
        "learning_weight": round(weight, 4),
    }
