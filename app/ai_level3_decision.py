# app/ai_level3_decision.py
from typing import Dict, Any
from app.ai_level2_scoring import passes_money_filter

def decide_action(deal: Dict[str, Any], scores: Dict[str, float]) -> str:
    """
    Returns: ignore, review, contact_seller, notify_buyers
    """
    if not passes_money_filter(scores):
        return "ignore"

    # High score => contact seller + notify buyers
    if scores["ai_score"] >= 80 and scores["risk_score"] <= 30:
        return "contact_seller"

    return "review"
