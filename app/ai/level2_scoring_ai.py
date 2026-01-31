import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/ai/score", tags=["ai-level2"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def fallback_ai_score(deal: dict) -> dict:
    # smart-ish fallback until OPENAI is connected
    title = (deal.get("title") or "").lower()
    price = float(deal.get("price") or 0)

    profit_score = 60
    urgency_score = 55
    risk_score = 40

    if "urgent" in title or "must sell" in title:
        urgency_score = 85
    if price > 0 and price < 10000:
        profit_score = 75

    total = max(0, min(100, int((profit_score + urgency_score + (100 - risk_score)) / 3)))

    return {
        "profit_score": profit_score,
        "urgency_score": urgency_score,
        "risk_score": risk_score,
        "ai_score": total,
        "reasons": "AI scoring fallback (no OPENAI_API_KEY set)."
    }

@router.post("/{deal_id}")
def score_deal_ai(deal_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("select * from deals where id=%s", (deal_id,))
        deal = cur.fetchone()
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")

        # ✅ For now: fallback scoring (no external calls)
        s = fallback_ai_score(deal)

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
