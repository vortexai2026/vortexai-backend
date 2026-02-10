# app/ai_level2_scoring.py
from typing import Dict, Any


def score_deal(deal: Dict[str, Any]) -> Dict[str, float]:
    """
    LEVEL 2: Scoring AI (fast + stable, no OpenAI needed)
    Returns: profit_score, urgency_score, risk_score, ai_score
    """

    price = float(deal.get("price") or 0)
    title = (deal.get("title") or "").lower()
    location = (deal.get("location") or "").lower()
    asset_type = (deal.get("asset_type") or "").lower()

    profit = 0.0
    urgency = 0.0
    risk = 0.0

    # -----------------------------
    # Profit heuristics
    # -----------------------------
    if asset_type in ("real_estate", "house", "homes"):
        if 30000 <= price <= 200000:
            profit += 70
        elif 200000 < price <= 350000:
            profit += 55
        elif price > 350000:
            profit += 40
        else:
            profit += 25

    elif asset_type in ("cars", "car", "vehicle"):
        if 1000 <= price <= 5000:
            profit += 70
        elif 5000 < price <= 12000:
            profit += 55
        elif price > 12000:
            profit += 35
        else:
            profit += 20

    elif asset_type in ("business", "businesses"):
        if 10000 <= price <= 150000:
            profit += 65
        else:
            profit += 40

    else:
        profit += 35

    # -----------------------------
    # Urgency keywords
    # -----------------------------
    urgent_words = [
        "must sell", "urgent", "asap", "today", "need gone", "moving",
        "divorce", "foreclosure", "motivated", "price reduced", "reduced"
    ]
    if any(w in title for w in urgent_words):
        urgency += 70
    else:
        urgency += 30

    # -----------------------------
    # Risk keywords
    # -----------------------------
    risky_words = [
        "no title", "salvage", "rebuilt", "as-is", "scam", "cash only",
        "no paperwork", "needs work", "fire damage", "mould", "mold"
    ]
    if any(w in title for w in risky_words):
        risk += 65
    else:
        risk += 25

    # -----------------------------
    # Location boost (example)
    # -----------------------------
    if any(city in location for city in ["winnipeg", "toronto", "vancouver", "calgary", "edmonton"]):
        profit += 10

    # Clamp 0-100
    profit = max(0.0, min(100.0, profit))
    urgency = max(0.0, min(100.0, urgency))
    risk = max(0.0, min(100.0, risk))

    # Composite AI score (0-100)
    ai_score = (profit * 0.50) + (urgency * 0.35) - (risk * 0.20)
    ai_score = max(0.0, min(100.0, ai_score))

    return {
        "profit_score": round(profit, 2),
        "urgency_score": round(urgency, 2),
        "risk_score": round(risk, 2),
        "ai_score": round(ai_score, 2),
    }
