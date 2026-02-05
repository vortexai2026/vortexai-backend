# app/services/daily_report.py
from datetime import date
from app.db import db
from app.ai import ask_ai
from app.email import send_email

def send_daily_report():
    stats = db.fetch_one("""
      SELECT
        COUNT(*) AS deals_today,
        COUNT(*) FILTER (WHERE decision='contact_seller') AS contacted,
        COUNT(*) FILTER (WHERE ai_score > 80) AS hot_deals
      FROM deals
      WHERE created_at::date = CURRENT_DATE;
    """)

    summary = ask_ai(f"""
    Create a daily business summary:

    Deals found: {stats['deals_today']}
    Contacted: {stats['contacted']}
    Hot deals: {stats['hot_deals']}

    Include:
    - Best cities
    - What worked
    - What failed
    """)

    send_email(
        to="you@yourcompany.com",
        subject="VortexAI Daily Report",
        body=summary
    )
