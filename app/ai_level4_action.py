from typing import Dict, Any

def build_next_action(decision: str, deal: Dict[str, Any]) -> str:
    title = deal.get("title", "")
    source = deal.get("source", "")
    location = deal.get("location", "")

    if decision == "contact_now":
        return f"CONTACT SELLER: '{title}' from {source} in {location}"
    if decision == "review":
        return f"REVIEW DEAL: '{title}' (check comps, confirm details)"
    if decision == "watch":
        return f"WATCHLIST: '{title}' (wait for price drop / more info)"
    return f"REJECT: '{title}' (too risky)"
