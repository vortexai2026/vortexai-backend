from typing import Dict, Any


def decide_action(
    deal: Dict[str, Any],
    scores: Dict[str, float]
) -> Dict[str, Any]:
    """
    LEVEL 3 – DECISION AI

    Purpose:
    - Take Level 2 scores
    - Decide WHAT to do with the deal
    - No OpenAI required
    - Deterministic + stable

    Possible actions:
    - notify_buyers
    - queue_for_review
    - discard
    """

    ai_score = scores.get("ai_score", 0)
    profit = scores.get("profit_score", 0)
    urgency = scores.get("urgency_score", 0)
    risk = scores.get("risk_score", 0)

    # -----------------------------
    # DECISION RULES
    # -----------------------------

    # 🔥 HOT DEAL
    if ai_score >= 70 and profit >= 50 and risk <= 40:
        action = "notify_buyers"
        priority = "high"

    # 🟡 MAYBE DEAL
    elif ai_score >= 40 and risk <= 60:
        action = "queue_for_review"
        priority = "medium"

    # ❌ BAD DEAL
    else:
        action = "discard"
        priority = "low"

    # -----------------------------
    # RETURN DECISION
    # -----------------------------
    return {
        "action": action,
        "priority": priority,
        "ai_score": ai_score,
        "profit_score": profit,
        "urgency_score": urgency,
        "risk_score": risk,
    }
