# app/ai_level6_strategy.py
from typing import Dict, Any
from app.database import fetch_all

def strategy_summary() -> Dict[str, Any]:
    """
    Very simple trend summary: what asset types are producing best AI scores.
    """
    rows = fetch_all("""
        SELECT asset_type, COUNT(*) as total, AVG(ai_score) as avg_score
        FROM deals
        WHERE created_at > NOW() - INTERVAL '7 days'
        GROUP BY asset_type
        ORDER BY avg_score DESC
    """)
    return {"last_7_days": rows}
