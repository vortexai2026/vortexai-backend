from app.models.deal import Deal

def apply_scoring(deal: Deal):

    distressed_keywords = [
        "must sell",
        "as-is",
        "fixer",
        "cash only",
        "handyman",
        "estate",
        "vacant"
    ]

    text = (deal.title or "").lower()

    score = 0
    for word in distressed_keywords:
        if word in text:
            score += 10

    deal.score = score

    if score >= 20:
        deal.status = "GREEN"
    else:
        deal.status = "NEW"

    return deal
