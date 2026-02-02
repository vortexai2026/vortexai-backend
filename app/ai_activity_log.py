from datetime import datetime
from app.database import execute

def log_ai_action(level: int, action: str, reason: str, meta: dict = None):
    execute("""
        INSERT INTO ai_activity_log (level, action, reason, meta, created_at)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        level,
        action,
        reason,
        meta or {},
        datetime.utcnow()
    ))
