from app.database import fetch_all
from app.emailer import send_email

def daily_report():
    deals = fetch_all("SELECT COUNT(*) FROM deals")
    kept = fetch_all("SELECT COUNT(*) FROM deals WHERE ai_score >= 60")

    send_email(
        "📊 Daily AI Report",
        f"Total deals: {deals[0][0]}\nHot deals: {kept[0][0]}"
    )
