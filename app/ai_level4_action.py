from typing import Dict
from app.emailer import send_email


def build_next_action(deal: Dict) -> Dict:
    """
    LEVEL 4: Action AI
    Decides what to DO with a deal.
    """

    ai_score = deal.get("ai_score", 0)

    if ai_score >= 70:
        action = "notify"
        message = f"""
        <h3>🔥 HOT DEAL FOUND</h3>
        <p><b>Title:</b> {deal.get('title')}</p>
        <p><b>Price:</b> {deal.get('price')}</p>
        <p><b>Location:</b> {deal.get('location')}</p>
        <p><b>AI Score:</b> {ai_score}</p>
        """

        send_email(
            to_email=os.getenv("ALERT_EMAIL", "you@example.com"),
            subject="🔥 New Hot Deal Detected",
            html_content=message,
        )

    else:
        action = "ignore"

    return {
        "action": action,
        "ai_score": ai_score,
    }
