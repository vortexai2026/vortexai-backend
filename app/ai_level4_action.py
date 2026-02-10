# app/ai_level4_action.py
from typing import Dict, Any


def build_next_action(deal: Dict[str, Any], decision: str) -> Dict[str, Any]:
    """
    LEVEL 4: Action Builder (NO auto-messaging here)
    This returns structured actions your UI/worker can use.
    """

    asset_type = (deal.get("asset_type") or "").lower()
    url = deal.get("url") or ""
    title = deal.get("title") or ""
    location = deal.get("location") or ""
    price = deal.get("price")

    if decision == "ignore":
        return {
            "type": "ignore",
            "reason": "Not enough profit/urgency or too risky",
        }

    if decision == "review":
        return {
            "type": "review",
            "todo": [
                "Open link and verify listing is real",
                "Check comps quickly",
                "Decide if you want to contact seller",
            ],
            "deal": {"title": title, "location": location, "price": price, "url": url},
        }

    if decision == "contact_seller":
        return {
            "type": "contact_seller",
            "channel": "manual",
            "instructions": "Use Outreach Draft (copy/paste) to contact seller safely.",
            "deal": {"title": title, "location": location, "price": price, "url": url, "asset_type": asset_type},
        }

    if decision == "notify_buyers":
        return {
            "type": "notify_buyers",
            "instructions": "Send to matching buyers (when buyer system is added).",
            "deal": {"title": title, "location": location, "price": price, "url": url, "asset_type": asset_type},
        }

    return {"type": "unknown", "decision": decision}
