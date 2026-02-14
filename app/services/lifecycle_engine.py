from datetime import datetime, timezone


ALLOWED_TRANSITIONS = {
    "new": ["ai_processed", "dead"],
    "ai_processed": ["matched", "dead"],
    "matched": ["contacted", "dead"],
    "contacted": ["under_contract", "dead"],
    "under_contract": ["closed", "dead"],
    "closed": [],
    "dead": []
}


def validate_transition(current_status: str, new_status: str):
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Invalid transition from '{current_status}' to '{new_status}'"
        )


def apply_transition_side_effects(deal, new_status, buyer=None):
    deal.status = new_status
    deal.updated_at = datetime.now(timezone.utc)

    if new_status == "matched" and buyer:
        deal.matched_buyer_id = buyer.id
        buyer.total_matches += 1

    if new_status == "closed":
        if deal.assignment_fee:
            deal.actual_profit = deal.assignment_fee
        if buyer:
            buyer.total_deals_closed += 1
