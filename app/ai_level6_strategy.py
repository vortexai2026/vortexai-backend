from typing import Dict, List
from app.database import fetch_all

"""
LEVEL 6: Strategy AI
Reads outcomes + deal history and suggests strategy changes.
Simple stable version (no OpenAI required).
"""

DEFAULT_STRATEGY = {
    "focus_asset_types": ["real_estate", "cars", "businesses"],
    "min_ai_score": 60,
    "max_risk": 70,
}

def strategy_summary() -> Dict:
    rows = fetch_all("""
        SELECT outcome, count(*) as cnt
        FROM outcomes
        GROUP BY outcome
        ORDER BY cnt DESC
    """)

    stats = {r["outcome"]: int(r["cnt"]) for r in rows} if rows else {}
    wins = sum(stats.get(k, 0) for k in ["sold", "closed", "profit"])
    losses = sum(stats.get(k, 0) for k in ["failed", "scam", "loss"])

    strategy = dict(DEFAULT_STRATEGY)

    # if losses high, tighten filters
    if losses > wins and losses >= 3:
        strategy["min_ai_score"] = 70
        strategy["max_risk"] = 60

    # if wins are strong, loosen a little to capture more volume
    if wins >= 5 and wins > losses:
        strategy["min_ai_score"] = 55

    return {
        "stats": stats,
        "wins": wins,
        "losses": losses,
        "strategy": strategy
    }
