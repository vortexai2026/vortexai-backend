def learn_adjustment(outcome: str) -> float:
    """
    Level 5 Learning AI
    Adjusts future scoring weights
    """

    outcome = (outcome or "").lower()

    if outcome in ("sold", "closed", "profit"):
        return 0.10

    if outcome in ("failed", "loss", "scam"):
        return -0.10

    return 0.0
