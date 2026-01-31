def score_deal(deal: dict) -> dict:
    score = 0

    price = float(deal.get("price") or 0)
    mv = float(deal.get("market_value") or 0)

    if mv > 0 and price < mv:
        score += 35

    motivation = (deal.get("motivation") or "").lower()
    if motivation in ("high", "urgent", "motivated"):
        score += 25

    dom = deal.get("days_on_market")
    if isinstance(dom, int) and dom < 14:
        score += 15

    asset_type = (deal.get("asset_type") or "").lower()
    if asset_type in ("real_estate", "cars", "business", "luxury"):
        score += 10

    # clamp
    score = max(0, min(100, score))
    grade = "GREEN" if score >= 75 else "YELLOW" if score >= 50 else "RED"

    return {
        **deal,
        "ai_score": score,
        "grade": grade,
        "risk_score": 100 - score
    }
