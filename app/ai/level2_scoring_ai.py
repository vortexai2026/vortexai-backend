from typing import Dict, Any

def score_deal(deal: Dict[str, Any]) -> Dict[str, float]:
    """
    Level 2: simple scoring (works without OpenAI).
    Later we plug in real AI (GPT) but this is stable and fast.
    """

    price = float(deal.get("price") or 0)
    title = (deal.get("title") or "").lower()
    location = (deal.get("location") or "").lower()
    asset_type = (deal.get("asset_type") or "").lower()

    profit = 0
    urgency = 0
    risk = 0

    # Profit heuristics
    if asset_type == "real_estate":
        if 50000 <= price <= 250000:
            profit += 60
        elif price > 250000:
            profit += 40
        else:
            profit += 25

    if asset_type in ("cars", "car"):
        if 1000 <= price <= 12000:
            profit += 60
        elif price <= 1000:
            risk += 20
        else:
            profit += 35

    # Urgency keywords
    urgent_words = ["must sell", "urgent", "asap", "today", "need gone", "moving", "divorce", "foreclosure"]
    if any(w in title for w in urgent_words):
        urgency += 60
    else:
        urgency += 25

    # Risk keywords
    risky_words = ["no title", "salvage", "rebuilt", "as-is", "scam", "cash only", "no paperwork"]
    if any(w in title for w in risky_words):
        risk += 60
    else:
        risk += 20

    # Location boost example
    if "winnipeg" in location or "toronto" in location or "vancouver" in location:
        profit += 10

    # Clamp 0-100
    profit = max(0, min(100, profit))
    urgency = max(0, min(100, urgency))
    risk = max(0, min(100, risk))

    ai_score = max(0, min(100, (profit * 0.5) + (urgency * 0.3) - (risk * 0.2)))

    return {
        "profit_score": round(profit, 2),
        "urgency_score": round(urgency, 2),
        "risk_score": round(risk, 2),
        "ai_score": round(ai_score, 2),
    }
