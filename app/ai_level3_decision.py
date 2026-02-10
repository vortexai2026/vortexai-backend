# app/ai_level3_decision.py
from typing import Dict, Any


def decide_action(deal: Dict[str, Any], scores: Dict[str, float]) -> str:
    """
    LEVEL 3: Decision AI
    Returns one of:
      - ignore
      - review
      - contact_seller
      - notify_buyers
    """

    profit = float(scores.get("profit_score", 0))
    urgency = float(scores.get("urgency_score", 0))
    risk = float(scores.get("risk_score", 0))
    ai_score = float(scores.get("ai_score", 0))

    # HARD MONEY RULES (your $1k-$25k/day logic)
    # Keep only deals worth action
    if urgency >= 60 and profit >= 60 and risk <= 40:
        return "contact_seller"

    # borderline deals (still show you)
    if ai_score >= 55 and risk <= 55:
        return "review"

    return "ignore"
