# app/daily_report.py
from app.database import fetch_all
from app.emailer import send_email

def send_daily_report():
    deals = fetch_all("""
        SELECT * FROM deals
        WHERE created_at > NOW() - INTERVAL '24 hours'
        ORDER BY ai_score DESC
    """)

    body = f"Daily AI Report\n\nTotal deals: {len(deals)}\n\n"

    for d in deals[:10]:
        body += f"""
{d['title']}
Score: {d['ai_score']}
Decision: {d['decision']}
Price: {d['price']}
Location: {d['location']}
-------------------
"""

    send_email("📊 VortexAI Daily Report", body)
