from typing import Dict, Any

def score_deal(deal: Dict[str, Any]) -> Dict[str, float]:
    price = float(deal.get("price") or 0)
    title = (deal.get("title") or "").lower()
    location = (deal.get("location") or "").lower()
    asset_type = (deal.get("asset_type") or "").lower()

    profit = 0
    urgency = 0
    risk = 0

    # Profit heuristics
    if asset_type == "real_estate":
        if 30000 <= price <= 200000:
            profit += 70
        elif price > 200000:
            profit += 45
        else:
            profit += 25

    if asset_type in ("cars", "car", "vehicle"):
        if 1000 <= price <= 5000:
            profit += 70
        elif price <= 1000:
            risk += 25
        else:
            profit += 40

    if asset_type in ("business", "businesses"):
        if 20000 <= price <= 250000:
            profit += 65
        else:
            profit += 35

    # Urgency keywords
    urgent_words = ["must sell", "urgent", "asap", "today", "need gone", "moving", "divorce", "foreclosure", "cash only"]
    urgency += 70 if any(w in title for w in urgent_words) else 30

    # Risk keywords
    risky_words = ["no title", "salvage", "rebuilt", "as-is", "scam", "no paperwork", "parts only"]
    risk += 70 if any(w in title for w in risky_words) else 20

    # Location boost
    hot_locations = ["winnipeg", "toronto", "vancouver", "calgary", "edmonton", "miami", "orlando", "houston", "dallas"]
    if any(city in location for city in hot_locations):
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
