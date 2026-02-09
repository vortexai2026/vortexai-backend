from app.database import fetch_all
from app.emailer import send_email
import os
from datetime import datetime, timedelta

OWNER_EMAIL = os.getenv("OWNER_EMAIL", "you@example.com")


def send_daily_report():
    """
    Sends a simple daily activity report.
    Safe to run via cron / background task.
    """

    since = datetime.utcnow() - timedelta(days=1)

    deals = fetch_all(
        """
        SELECT asset_type, decision, COUNT(*) as count
        FROM deals
        WHERE created_at >= %s
        GROUP BY asset_type, decision
        """,
        (since,)
    )

    body = "VortexAI Daily Report (Last 24h)\n\n"

    if not deals:
        body += "No activity in the last 24 hours.\n"
    else:
        for row in deals:
            body += f"- {row['asset_type']} | {row['decision']} → {row['count']}\n"

    send_email(
        to_email=OWNER_EMAIL,
        subject="VortexAI Daily Report",
        body=body
    )

    return {"ok": True}
