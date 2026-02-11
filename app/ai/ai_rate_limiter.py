from app.database import fetch_one
from datetime import datetime, timedelta

def can_act() -> bool:
    count = fetch_one("""
        SELECT COUNT(*) as c
        FROM ai_activity_log
        WHERE created_at > NOW() - INTERVAL '15 minutes'
    """)["c"]

    return count < 100
