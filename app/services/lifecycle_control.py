from typing import Dict, Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal

# Keep it simple and strict
ALLOWED: Dict[str, Set[str]] = {
    "NEW": {"SCORED", "DEAD"},
    "SCORED": {"CONTACTED", "DEAD"},
    "CONTACTED": {"NEGOTIATING", "DEAD"},
    "NEGOTIATING": {"OFFER_SENT", "FOLLOW_UP", "DEAD"},
    "FOLLOW_UP": {"NEGOTIATING", "DEAD"},
    "OFFER_SENT": {"UNDER_CONTRACT", "FOLLOW_UP", "DEAD"},
    "UNDER_CONTRACT": {"BLASTED", "ASSIGNED", "DEAD"},
    "BLASTED": {"ASSIGNED", "DEAD"},
    "ASSIGNED": {"CLOSED", "DEAD"},
    "CLOSED": set(),
    "DEAD": set(),
}

def can_transition(frm: str, to: str) -> bool:
    frm = (frm or "NEW").upper()
    to = (to or "").upper()
    return to in ALLOWED.get(frm, set())

async def set_status(db: AsyncSession, deal: Deal, new_status: str) -> None:
    new_status = (new_status or "").upper()
    cur = (deal.status or "NEW").upper()

    if cur == new_status:
        return

    if not can_transition(cur, new_status):
        raise ValueError(f"Invalid lifecycle transition: {cur} -> {new_status}")

    deal.status = new_status
    await db.commit()
