import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException

DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/ai/decision", tags=["ai-level3"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def decide(ai_score: int) -> str:
    if ai_score >= 85:
        return "auto_approve"
    if ai_score >= 70:
        return "review"
    return "reject"

@router.post("/{deal_id}")
def decide_for_deal(deal_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("select * from ai_scores where deal_id=%s", (deal_id,))
        score = cur.fetchone()
        if not score:
            raise HTTPException(status_code=400, detail="Run Level 1/2 scoring first")

        action = decide(int(score["ai_score"] or 0))

        # store decision as action
        action_id = str(uuid.uuid4())
        cur.execute("""
            insert into ai_actions (id, deal_id, action, status, payload)
            values (%s,%s,%s,'queued',%s::jsonb)
        """, (action_id, deal_id, action, "{}"))

        # optional update deal status
        if action == "auto_approve":
            cur.execute("update deals set status='approved' where id=%s", (deal_id,))
        elif action == "reject":
            cur.execute("update deals set status='rejected' where id=%s", (deal_id,))
        else:
            cur.execute("update deals set status='review' where id=%s", (deal_id,))

        conn.commit()
        return {"deal_id": deal_id, "decision": action, "action_id": action_id}
    finally:
        conn.close()
