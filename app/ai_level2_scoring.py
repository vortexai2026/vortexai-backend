from typing import Dict, Any


def score_deal(deal: Dict[str, Any]) -> Dict[str, float]:
    """
    LEVEL 2 – DEAL SCORING AI (NO OPENAI REQUIRED)

    Purpose:
    - Score deals based on simple, reliable rules
    - Fast, stable, production-safe
    - Later you can replace logic with GPT if you want

    Input:
    deal = {
        "title": str,
        "price": float,
        "location": str,
        "asset_type": str
    }

    Output:
    {
        "profit_score": 0–100,
        "urgency_score": 0–100,
        "risk_score": 0–100,
        "ai_score": 0–100
    }
    """

    # -----------------------------
    # SAFE INPUT EXTRACTION
    # -----------------------------
    price = float(deal.get("price") or 0)
    title = (deal.get("title") or "").lower()
    location = (deal.get("location") or "").lower()
    asset_type = (deal.get("asset_type") or "").lower()

    profit = 0
    urgency = 0
    risk = 0

    # -----------------------------
    # PROFIT HEURISTICS
    # -----------------------------
    if asset_type == "real_estate":
        if 50000 <= price <= 250000:
            profit += 60
        elif price > 250000:
            profit += 40
        else:
            profit += 25

    if asset_type in ("car", "cars"):
        if 1000 <= price <= 12000:
            profit += 60
        elif price < 1000:
            risk += 25
        else:
            profit += 35

    if asset_type in ("business", "businesses"):
        if price <= 50000:
            profit += 55
        else:
            profit += 40

    # -----------------------------
    # URGENCY KEYWORDS
    # -----------------------------
    urgent_words = [
        "urgent",
        "must sell",
        "asap",
        "today",
        "need gone",
        "moving",
        "divorce",
        "foreclosure"
    ]

    if any(word in title for word in urgent_words):
        urgency += 60
    else:
        urgency += 25

    # -----------------------------
    # RISK KEYWORDS
    # -----------------------------
    risky_words = [
        "no title",
        "salvage",
        "rebuilt",
        "as-is",
        "scam",
        "cash only",
        "no paperwork"
    ]

    if any(word in title for word in risky_words):
        risk += 60
    else:
        risk += 20

    # -----------------------------
    # LOCATION BOOST
    # -----------------------------
    hot_locations = [
        "winnipeg",
        "toronto",
        "vancouver",
        "calgary",
        "edmonton",
        "new york",
        "los angeles",
        "miami",
        "houston",
        "phoenix"
    ]

    if any(city in location for city in hot_locations):
        profit += 10

    # -----------------------------
    # CLAMP VALUES (0–100)
    # -----------------------------
    profit = max(0, min(100, profit))
    urgency = max(0, min(100, urgency))
    risk = max(0, min(100, risk))

    # -----------------------------
    # FINAL AI SCORE
    # -----------------------------
    ai_score = (profit * 0.5) + (urgency * 0.3) - (risk * 0.2)
    ai_score = max(0, min(100, ai_score))

    return {
        "profit_score": round(profit, 2),
        "urgency_score": round(urgency, 2),
        "risk_score": round(risk, 2),
        "ai_score": round(ai_score, 2),
    }
