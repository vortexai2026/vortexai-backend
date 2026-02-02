# app/ai_level4_action.py

from typing import Dict, Any
from app.emailer import send_email

"""
LEVEL 4 — ACTION AI

This layer decides WHAT TO DO next with a deal:
- notify you
- escalate
- ignore
- mark for follow-up

This MUST expose: build_next_action()
"""


def build_next_action(deal: Dict[str, Any], scores: Dict[str, float]) -> Dict[str, Any]:
    """
    Decide the next action based on AI scores.
    This function is REQUIRED by deals_routes.py
    """

    profit = scores.get("profit_score", 0)
    urgency = scores.get("urgency_score", 0)
    risk = scores.get("risk_score", 100)
    ai_score = scores.get("ai_score", 0)

    action = "ignore"
    reason = "Low score"

    # 🟢 HIGH VALUE DEAL → IMMEDIATE ACTION
    if profit >= 60 and urgency >= 60 and risk <= 40:
        action = "notify_now"
        reason = "High profit & urgency, low risk"

        send_email(
            to_email="youremail@domain.com",  # change later
            subject="🔥 HOT DEAL FOUND",
            body=f"""
HOT DEAL DETECTED

Title: {deal.get('title')}
Price: {deal.get('price')}
Location: {deal.get('location')}

Profit: {profit}
Urgency: {urgency}
Risk: {risk}
AI Score: {ai_score}

TAKE ACTION NOW.
"""
        )

    # 🟡 MEDIUM DEAL → FOLLOW UP
    elif profit >= 50 and urgency >= 40 and risk <= 50:
        action = "follow_up"
        reason = "Decent deal, monitor"

    # 🔴 BAD DEAL → IGNORE
    else:
        action = "ignore"
        reason = "Does not meet thresholds"

    return {
        "action": action,
        "reason": reason,
        "scores": scores
    }
