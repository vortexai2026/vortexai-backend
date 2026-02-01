from typing import Dict, Any
from datetime import datetime, timezone
from app.database import execute, fetch_one


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def learn_adjustment(outcome: str) -> float:
    """
    outcome examples:
    sold / closed / profit -> +0.10
    failed / scam / loss -> -0.10
    unknown -> 0.0
    """
    o = (outcome or "").strip().lower()
    if o in ("sold", "closed", "profit", "success"):
        return 0.10
    if o in ("failed", "scam", "loss", "bad"):
        return -0.10
    return 0.0


def record_outcome(deal_id: str, outcome: str, notes: str = "") -> Dict[str, Any]:
    """
    LEVEL 5 – LEARNING AI

    Purpose:
    - Store outcome for a deal
    - Update a small learning table (weights) based on outcome
    """

    deal_id = (deal_id or "").strip()
    if not deal_id:
        return {"ok": False, "error": "deal_id required"}

    adj = learn_adjustment(outcome)

    # Save outcome on deals table
    execute(
        """
        UPDATE deals
        SET outcome=%s, outcome_notes=%s, updated_at=%s
        WHERE id=%s
        """,
        (outcome, notes, _utc_now(), deal_id),
    )

    # Use a single global weight record
    row = fetch_one("SELECT id, weight FROM learning_weights LIMIT 1", ())
    if not row:
        execute(
            "INSERT INTO learning_weights (id, weight, updated_at) VALUES (%s,%s,%s)",
            ("global", 1.0 + adj, _utc_now()),
        )
        new_weight = 1.0 + adj
    else:
        new_weight = float(row.get("weight") or 1.0) + adj
        execute(
            "UPDATE learning_weights SET weight=%s, updated_at=%s WHERE id=%s",
            (new_weight, _utc_now(), str(row["id"])),
        )

    return {
        "ok": True,
        "deal_id": deal_id,
        "outcome": outcome,
        "adjustment": adj,
        "new_global_weight": round(new_weight, 4),
    }
