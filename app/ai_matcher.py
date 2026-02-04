# app/ai_matcher.py
from typing import List, Dict
from app.database import fetch_all

def match_buyers(deal: Dict) -> List[Dict]:
    buyers = fetch_all("""
        SELECT * FROM buyers
        WHERE %s = ANY(asset_types)
        AND min_price <= %s
        AND max_price >= %s
    """, (
        deal["asset_type"],
        deal["price"] or 0,
        deal["price"] or 0
    ))
    return buyers
