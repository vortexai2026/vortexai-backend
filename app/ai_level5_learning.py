# app/ai_level5_learning.py
import uuid
import json
from typing import Dict, Any
from app.database import execute


def learn_adjustment(deal_id: str, decision: str, scores: Dict[str, float]) -> None:
    """
    LEVEL 5: Learning log
    Saves a learning event so Level 6 can analyze.
    """
    try:
        execute(
            """
            INSERT INTO learning_events (id, deal_id, event_type, metadata)
            VALUES (%s, %s, %s, %s::jsonb)
            """,
            (
                str(uuid.uuid4()),
                deal_id,
                "auto_scored",
                json.dumps({"decision": decision, "scores": scores}),
            ),
        )
    except Exception:
        # don't break deal ingestion if learning fails
        return
