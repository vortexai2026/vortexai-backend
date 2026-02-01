from typing import Dict

def decide_action(scores: Dict[str, float]) -> str:
    """
    Level 3 Decision AI
    """

    profit = scores.get("profit_score", 0)
    urgency = scores.get("urgency_score", 0)
    risk = scores.get("risk_score", 0)
    ai_score = scores.get("ai_score", 0)

    if ai_score >= 60 and profit >= 60 and risk <= 30:
        return "hot"

    if ai_score >= 40 and risk <= 50:
        return "review"

    return "reject"
