from typing import Dict, Any

def decide_next_action(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Level 3: decision AI - what should we do next?
    """

    score = float(deal.get("ai_score") or 0)
    risk = float(deal.get("risk_score") or 0)

    if risk >= 75:
        return {"decision": "reject", "reason": "risk too high"}
    if score >= 75:
        return {"decision": "push", "reason": "high score - notify VIP buyers"}
    if score >= 55:
        return {"decision": "review", "reason": "medium score - send to manual review"}
    return {"decision": "hold", "reason": "low score - keep but don't notify"}
