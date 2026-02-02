from typing import Dict, Any

def score_deal(deal: Dict[str, Any]) -> Dict[str, float]:
    price = float(deal.get("price") or 0)
    title = (deal.get("title") or "").lower()
    location = (deal.get("location") or "").lower()
    asset_type = (deal.get("asset_type") or "").lower()

    profit = 0
    urgency = 0
    risk = 0

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

    urgent_words = ["must sell", "urgent", "asap", "today", "need gone", "moving", "divorce", "foreclosure"]
    urgency += 60 if any(w in title for w in urgent_words) else 25

    risky_words = ["no title", "salvage", "rebuilt", "as-is", "scam", "cash only", "no paperwork"]
    risk += 60 if any(w in title for w in risky_words) else 20

    if any(x in location for x in ["winnipeg", "toronto", "vancouver", "new york", "los angeles", "miami"]):
        profit += 10

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
