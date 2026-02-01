def learn_adjustment(outcome: str) -> float:
    outcome = (outcome or "").lower()
    if outcome in ("sold", "closed", "profit"):
        return 0.10
    if outcome in ("failed", "scam", "loss"):
        return -0.10
    return 0.0
