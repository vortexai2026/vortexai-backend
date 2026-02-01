from typing import Dict, Any, List

def match_buyers_stub(deal: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Level 4: action AI - match to buyers.
    This is a stub: later we match from DB buyers table.
    """
    # For now just returns a placeholder match list
    return [{"buyer_email": "vip@example.com", "match_reason": "stub match"}]

def action_plan(deal: Dict[str, Any]) -> Dict[str, Any]:
    decision = deal.get("decision", "hold")

    if decision == "push":
        return {"action": "notify", "channel": ["email", "sms"], "priority": "high"}
    if decision == "review":
        return {"action": "queue_manual_review", "priority": "medium"}
    if decision == "reject":
        return {"action": "archive", "priority": "low"}
    return {"action": "hold", "priority": "low"}
