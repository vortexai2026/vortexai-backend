import os
import uuid
import psycopg2
from fastapi import APIRouter
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/ai/learn", tags=["ai-level5"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

class Feedback(BaseModel):
    outcome: str  # "sold_fast" | "no_interest" | "bad_lead" | "closed"
    profit_real: float | None = None
    notes: str | None = None

@router.post("/{deal_id}")
def submit_feedback(deal_id: str, fb: Feedback):
    conn = get_conn()
    try:
        cur = conn.cursor()
        fid = str(uuid.uuid4())
        cur.execute("""
            insert into ai_feedback (id, deal_id, outcome, profit_real, notes)
            values (%s,%s,%s,%s,%s)
        """, (fid, deal_id, fb.outcome, fb.profit_real, fb.notes))

        # simple learning: update weights based on outcome
        if fb.outcome in ("sold_fast", "closed"):
            cur.execute("""
                update ai_weights set
                  w_profit = least(0.70, w_profit + 0.02),
                  w_urgency = least(0.40, w_urgency + 0.01),
                  w_risk = greatest(0.10, w_risk - 0.01),
                  updated_at=now()
                where id=1
            """)
        elif fb.outcome in ("no_interest", "bad_lead"):
            cur.execute("""
                update ai_weights set
                  w_risk = least(0.60, w_risk + 0.02),
                  updated_at=now()
                where id=1
            """)

        conn.commit()
        return {"ok": True, "feedback_id": fid}
    finally:
        conn.close()
