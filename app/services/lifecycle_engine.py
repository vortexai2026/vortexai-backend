from fastapi import HTTPException
from datetime import datetime, timezone
from app.models.deal import Deal


ALLOWED_TRANSITIONS = {
    "new": ["matched", "rejected"],
    "matched": ["contacted", "closed", "cancelled"],
    "contacted": ["closed", "cancelled"],
    "closed": [],
    "rejected": [],
    "cancelled": []
}


def validate_transition(current_status: str, new_status: str):
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])

    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_status} → {new_status}"
        )


def apply_transition(deal: Deal, new_status: str):
    validate_transition(deal.status, new_status)

    deal.status = new_status
    deal.updated_at = datetime.now(timezone.utc)

    return deal
