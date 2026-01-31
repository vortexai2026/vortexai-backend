import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException

DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter(prefix="/ai/rules", tags=["ai-level1"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def compute_rule_score(deal: dict) -> dict:
    """
    Simple rule scoring when you don't want AI calls.
    """
    price = float(deal.get("price") or 0)
    ai_score = int(deal.get("ai_score") or 0)

    profit_score = 70 if price > 0 else 10
    urgency_score = 50
    risk_score = 30 if ai_score >= 75 else 60

    # total
    total = max(0, min(100, int((profit_score + urgency_score + (100 - risk_score)) / 3)))

    return {
        "profit_score": profit_score,
        "urgency_score": urgency_score,
        "risk_score": risk_score,
        "ai_score": total,
        "reasons": "Rule-based scoring (no AI call)."
    }

@router.post("/score/{deal_id}")
def rule_score_deal(deal_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("select * from deals where id=%s", (deal_id,))
        deal = cur.fetchone()
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")

        s = compute_rule_score(deal)

        cur.execute("""
            insert into ai_scores (deal_id, profit_score, urgency_score, risk_score, ai_score, reasons)
            values (%s,%s,%s,%s,%s,%s)
            on conflict (deal_id) do update set
              profit_score=excluded.profit_score,
              urgency_score=excluded.urgency_score,
              risk_score=excluded.risk_score,
              ai_score=excluded.ai_score,
              reasons=excluded.reasons,
              scored_at=now()
        """, (deal_id, s["profit_score"], s["urgency_score"], s["risk_score"], s["ai_score"], s["reasons"]))

        conn.commit()
        return {"deal_id": deal_id, **s}
    finally:
        conn.close()
