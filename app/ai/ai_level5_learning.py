from typing import Dict
from app.database import execute
import uuid
import json

def learn_adjustment(deal_id: str, decision: str, scores: Dict[str, float]) -> None:
    # For now we log learning events. Later you can update thresholds automatically.
    execute("""
        INSERT INTO learning_events (id, deal_id, event_type, metadata)
        VALUES (%s,%s,%s,%s::jsonb)
    """, (
        str(uuid.uuid4()),
        deal_id,
        "scored",
        json.dumps({"decision": decision, "scores": scores})
    ))
