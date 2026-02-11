from app.database import fetch_one
from app.ai_activity_log import log_ai_action

def failsafe_check():
    errors = fetch_one("""
        SELECT COUNT(*) as c
        FROM ai_activity_log
        WHERE action LIKE '%error%'
        AND created_at > NOW() - INTERVAL '1 hour'
    """)["c"]

    if errors > 10:
        log_ai_action(
            level=0,
            action="SYSTEM_PAUSED",
            reason="Too many errors detected"
        )
        raise RuntimeError("Failsafe triggered")
