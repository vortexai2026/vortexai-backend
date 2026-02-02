import time
from app.database import fetch_all, execute
from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import build_next_action

"""
LEVEL 7: Orchestrator
Loops through new deals -> scores -> decision -> next action -> updates DB
"""

def process_once(limit: int = 50):
    deals = fetch_all("""
        SELECT * FROM deals
        WHERE status='new'
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    for d in deals:
        deal = dict(d)

        scores = score_deal(deal)
        decision = decide_action(scores, deal)
        next_action = build_next_action(decision, deal)

        execute("""
            UPDATE deals
            SET profit_score=%s,
                urgency_score=%s,
                risk_score=%s,
                ai_score=%s,
                decision=%s,
                next_action=%s,
                status=%s
            WHERE id=%s
        """, (
            scores["profit_score"],
            scores["urgency_score"],
            scores["risk_score"],
            scores["ai_score"],
            decision,
            next_action,
            "processed",
            str(deal["id"])
        ))

def run_forever():
    while True:
        process_once()
        time.sleep(10)

if __name__ == "__main__":
    run_forever()
