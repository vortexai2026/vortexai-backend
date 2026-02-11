import os
import time
from app.database import fetch_all, execute
from app.ai_scoring import score_deal

AUTOMATE_EVERY_SECONDS = int(os.getenv("AUTOMATE_EVERY_SECONDS", "300"))

def run_once():
    deals = fetch_all("""
        SELECT * FROM deals
        ORDER BY created_at DESC
        LIMIT 50
    """)

    for d in deals:
        scored = score_deal(d)
        execute("""
            UPDATE deals
            SET ai_score=%s, risk_score=%s, grade=%s
            WHERE id=%s
        """, (scored["ai_score"], scored["risk_score"], scored["grade"], scored["id"]))
        print("Scored", scored["id"], scored["ai_score"], scored["grade"])

def loop():
    while True:
        run_once()
        time.sleep(AUTOMATE_EVERY_SECONDS)

if __name__ == "__main__":
    loop()
