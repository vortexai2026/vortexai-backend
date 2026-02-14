from app.models.deal import Deal

DISTRESSED_KEYWORDS = [
    "must sell",
    "as-is",
    "fixer",
    "cash only",
    "handyman",
    "estate",
    "vacant"
]

def score_deal(deal: Deal):
    """
    Main scoring function used by ai_processor.
    Keeps compatibility with existing imports.
    """

    text = (deal.title or "").lower()

    score = 0
    for word in DISTRESSED_KEYWORDS:
        if word in text:
            score += 10

    deal.score = score

    if score >= 20:
        deal.status = "GREEN"
    else:
        deal.status = "NEW"

    return deal
