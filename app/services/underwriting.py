def confidence_score(arv: float, repairs: float, seller_asking: float | None) -> int:
    """
    MVP confidence:
    - higher ARV, reasonable repairs, asking below MAO => higher score
    """
    score = 40
    if arv and arv > 150000:
        score += 10
    if repairs is not None:
        if repairs <= 25000:
            score += 15
        elif repairs <= 50000:
            score += 8
    if seller_asking is not None and arv:
        if seller_asking < (arv * 0.65):
            score += 20
        elif seller_asking < (arv * 0.70):
            score += 10
    return max(0, min(100, score))
