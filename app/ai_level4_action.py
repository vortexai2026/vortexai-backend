# app/ai_level4_action.py
from typing import Dict, Any
from app.emailer import send_email

def build_next_action(deal: Dict[str, Any], decision: str) -> Dict[str, Any]:
    """
    Creates an action plan. Real messaging automation can be added later.
    """
    if decision == "ignore":
        return {"type": "none"}

    if decision == "review":
        return {
            "type": "review",
            "todo": [
                "Check listing URL",
                "Verify price/condition",
                "Decide if we contact seller"
            ]
        }

    if decision == "contact_seller":
        msg = (
            f"New HOT deal found\n\n"
            f"Title: {deal.get('title')}\n"
            f"Price: {deal.get('price')} {deal.get('currency')}\n"
            f"Location: {deal.get('location')}\n"
            f"URL: {deal.get('url')}\n\n"
            f"Suggested first message:\n"
            f"Hi! Is this still available? If yes, what’s the best cash price and how soon do you need to sell?"
        )
        send_email("🔥 VortexAI Hot Deal", msg)
        return {
            "type": "contact_seller",
            "message_template": "Hi! Is this still available? If yes, what’s the best cash price and how soon do you need to sell?",
            "notify": True
        }

    return {"type": "none"}
