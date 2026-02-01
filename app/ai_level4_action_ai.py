def next_action(decision: str) -> str:
    """
    Level 4 Action AI
    """

    if decision == "hot":
        return "notify_buyers"

    if decision == "review":
        return "manual_review"

    return "discard"
