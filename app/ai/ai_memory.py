from datetime import datetime
from app.database import execute

def remember(key: str, value: dict, confidence: float = 0.5):
    execute("""
        INSERT INTO ai_memory (key, value, confidence, created_at)
        VALUES (%s,%s,%s,%s)
    """, (key, value, confidence, datetime.utcnow()))
