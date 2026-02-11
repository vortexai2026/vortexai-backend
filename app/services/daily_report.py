# app/services/daily_report.py

from datetime import date
from app.database import fetch_one
from app.ai.ai_command_center import ask_ai
from app.services.emailer import send_email


def send_daily_report():
    """
    Generates a daily business summary using AI and emails it.
    This should be triggered by a worker or cron job.
    """

    # Fetch key stats for today
    stats = fetch_one("""
        SELECT
            COUNT(*) AS deals_today,
            COUNT(*) FILTER (WHERE decision = 'contact_seller') AS contacted,
            COUNT(*) FILTER (WHERE ai_score > 80) AS hot_deals
        FROM deals
        WHERE created_at::date = CURRENT_DATE;
    """)

    # Fallback if DB returns None
    if not stats:
        stats = {
            "deals_today": 0,
            "contacted": 0,
            "hot_deals": 0
        }

    # Ask AI to generate a narrative summary
    summary = ask_ai(f"""
    Create a concise, professional daily business summary for VortexAI.

    Stats for {date.today().isoformat()}:
    - Deals found: {stats['deals_today']}
    - Contacted sellers: {stats['contacted']}
    - Hot deals (AI score > 80): {stats['hot_deals']}

    Include:
    - Best performing cities
    - What worked today
    - What failed or underperformed
    - A short recommendation for tomorrow
    """)

    # Send the report
    send_email(
        to="you@yourcompany.com",
        subject="📊 VortexAI Daily Report",
        body=summary
    )

    return {"status": "sent", "stats": stats}

