from typing import Dict

def decide_action(deal: dict, scores: Dict[str, float]) -> str:
    profit = scores.get("profit_score", 0)
    urgency = scores.get("urgency_score", 0)
    risk = scores.get("risk_score", 100)

    # MONEY RULE
    if urgency >= 60 and profit >= 60 and risk <= 40:
        return "contact_seller"

    # borderline = human review
    if urgency >= 45 and profit >= 45 and risk <= 55:
        return "review"

    return "ignore"
