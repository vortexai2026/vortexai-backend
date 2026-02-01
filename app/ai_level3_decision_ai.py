# app/ai_level3_decision.py

from typing import Dict, Any


def decide_action(deal: Dict[str, Any], scores: Dict[str, float]) -> str:
    """
    LEVEL 3 — Decision AI
    Decide what to do with a deal based on AI scores.
    """

    ai_score = scores.get("ai_score", 0)
    profit = scores.get("profit_score", 0)
    risk = scores.get("risk_score", 0)

    # ❌ Reject dangerous deals
    if risk >= 70:
        return "reject"

    # 🔥 High-value deal → send to buyers
    if ai_score >= 70 and profit >= 50:
        return "match_buyers"

    # 🟡 Medium → manual review
    if 40 <= ai_score < 70:
        return "review"

    # 🧊 Low value → ignore
    return "ignore"
