# app/ai_level4_action.py

from typing import Dict, Any


def execute_action(deal: Dict[str, Any], decision: str) -> Dict[str, Any]:
    """
    LEVEL 4 — Action AI
    Executes actions based on Level 3 decision.
    """

    result = {
        "action": decision,
        "status": "pending",
        "notes": ""
    }

    if decision == "match_buyers":
        result["status"] = "matched"
        result["notes"] = "Deal sent to matching buyers"

    elif decision == "review":
        result["status"] = "review_queue"
        result["notes"] = "Deal sent for manual review"

    elif decision == "ignore":
        result["status"] = "ignored"
        result["notes"] = "Low-value deal ignored"

    elif decision == "reject":
        result["status"] = "rejected"
        result["notes"] = "High risk detected"

    else:
        result["status"] = "unknown"
        result["notes"] = "Unhandled action"

    return result
