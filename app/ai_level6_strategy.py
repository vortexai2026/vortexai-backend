# app/ai_level6_strategy.py
from typing import Dict, Any
from app.database import fetch_all


def strategy_summary() -> Dict[str, Any]:
    """
    LEVEL 6: Strategy summary (simple analytics)
    Helps you see what AI is doing.
    """

    rows = fetch_all(
        """
        SELECT asset_type, decision, COUNT(*) as count
        FROM deals
        GROUP BY asset_type, decision
        ORDER BY count DESC
        """
    )

    return {
        "ok": True,
        "summary": rows,
        "notes": [
            "If too many ignores: adjust scoring thresholds",
            "If too many reviews: tighten decision rule",
            "If too few contact_seller: widen profitable ranges",
        ],
    }
