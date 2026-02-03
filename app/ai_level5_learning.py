# app/ai_level5_learning.py
from typing import Dict, Any
from app.database import execute

def learn_adjustment(deal_id: str, decision: str, scores: Dict[str, float]) -> None:
    """
    Logs learning events. Later you can use this to auto-tune thresholds.
    """
    execute("""
        INSERT INTO learning_events (id, deal_id, event_type, metadata)
        VALUES (gen_random_uuid(), %s, %s, %s::jsonb)
    """, (deal_id, "scored", f'{{"decision":"{decision}","scores":{scores}}}'))
