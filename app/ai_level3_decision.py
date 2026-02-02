from typing import Dict, Any

def decide_action(scores: Dict[str, float], deal: Dict[str, Any]) -> str:
    ai_score = float(scores.get("ai_score", 0))
    risk = float(scores.get("risk_score", 0))
    urgency = float(scores.get("urgency_score", 0))

    if risk >= 70:
        return "reject"
    if ai_score >= 75 and urgency >= 40:
        return "contact_now"
    if ai_score >= 60:
        return "review"
    return "watch"
