from app.database import fetch_all, execute
from app.ai_activity_log import log_ai_action

def run_strategy():
    stats = fetch_all("""
        SELECT asset_type, COUNT(*) as c
        FROM deals
        WHERE status='sold'
        GROUP BY asset_type
    """)

    for s in stats:
        if s["c"] > 10:
            execute("""
                UPDATE ai_strategy
                SET priority = priority + 1
                WHERE asset_type=%s
            """, (s["asset_type"],))

            log_ai_action(
                level=6,
                action="STRATEGY_BOOST",
                reason=f"Increasing focus on {s['asset_type']}"
            )
