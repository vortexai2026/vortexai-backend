# app/ai_level4_action.py

from typing import Dict, Any


def build_next_action(deal: Dict[str, Any], decision: str) -> Dict[str, Any]:
    """
    LEVEL 4 — ACTION PLANNER

    This function does NOT send messages.
    It only decides WHAT should happen next.
    Safe + controllable.

    Decisions supported:
    - contact_seller
    - review
    - ignore
    """

    asset_type = (deal.get("asset_type") or "").lower()
    price = deal.get("price") or 0
    location = (deal.get("location") or "").lower()

    # -------------------------
    # HIGH PRIORITY — CONTACT
    # -------------------------
    if decision == "contact_seller":
        return {
            "priority": "high",
            "action": "draft_outreach",
            "reason": "High profit + high urgency + acceptable risk",
            "recommended_channel": "manual",  # Facebook / Kijiji safe
            "next_steps": [
                "Generate outreach message",
                "Ask seller key questions",
                "Confirm availability",
                "Push to buyer matching if seller responds"
            ],
            "notes": f"Target asset_type={asset_type}, price={price}, location={location}"
        }

    # -------------------------
    # MEDIUM PRIORITY — REVIEW
    # -------------------------
    if decision == "review":
        return {
            "priority": "medium",
            "action": "manual_review",
            "reason": "Borderline deal — needs human confirmation",
            "next_steps": [
                "Check comps",
                "Verify seller story",
                "Confirm ownership / title",
                "Decide contact or ignore"
            ],
            "notes": f"Review asset_type={asset_type}, price={price}"
        }

    # -------------------------
    # LOW PRIORITY — IGNORE
    # -------------------------
    return {
        "priority": "low",
        "action": "ignore",
        "reason": "Low profit or high risk",
        "next_steps": [],
        "notes": "No further action required"
    }
