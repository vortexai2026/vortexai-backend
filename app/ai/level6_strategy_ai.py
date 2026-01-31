import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter

DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/ai/strategy", tags=["ai-level6"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@router.get("/summary")
def strategy_summary():
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("select count(*) as total from deals")
        total = cur.fetchone()["total"]

        cur.execute("select count(*) as approved from deals where status='approved'")
        approved = cur.fetchone()["approved"]

        cur.execute("""
            select count(*) as high_ai
            from ai_scores
            where ai_score >= 85
        """)
        high_ai = cur.fetchone()["high_ai"]

        suggestions = []
        if total > 0 and (approved / max(1, total)) < 0.2:
            suggestions.append("Your approval rate is low. Lower threshold from 85 → 80 temporarily.")
        if high_ai == 0:
            suggestions.append("No high AI deals found. Add more sources or adjust scoring weights.")
        if not suggestions:
            suggestions.append("System looks healthy. Increase automation: turn on Level 4 actions hourly.")

        return {
            "total_deals": total,
            "approved_deals": approved,
            "high_ai_deals": high_ai,
            "suggestions": suggestions
        }
    finally:
        conn.close()
