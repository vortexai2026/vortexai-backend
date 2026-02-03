# app/ai_level2_scoring.py
from typing import Dict, Any
import os

MIN_PROFIT = int(os.getenv("MIN_PROFIT", "60"))
MIN_URGENCY = int(os.getenv("MIN_URGENCY", "60"))
MAX_RISK = int(os.getenv("MAX_RISK", "40"))
MIN_AI_SCORE = int(os.getenv("MIN_AI_SCORE", "60"))

def score_deal(deal: Dict[str, Any]) -> Dict[str, float]:
    price = float(deal.get("price") or 0)
    title = (deal.get("title") or "").lower()
    location = (deal.get("location") or "").lower()
    asset_type = (deal.get("asset_type") or "").lower()

    profit = 0
    urgency = 0
    risk = 0

    # PROFIT rules by asset
    if asset_type == "real_estate":
        if 30000 <= price <= 200000:
            profit += 70
        elif 200000 < price <= 400000:
            profit += 55
        else:
            profit += 35

    if asset_type in ("cars", "car", "trucks"):
        if 1000 <= price <= 5000:
            profit += 75
        elif 5000 < price <= 12000:
            profit += 60
        else:
            profit += 40

    if asset_type in ("businesses", "business"):
        if 10000 <= price <= 150000:
            profit += 65
        else:
            profit += 45

    # URGENCY keywords
    urgent_words = ["must sell", "urgent", "asap", "today", "need gone", "moving", "divorce", "foreclosure", "cash only"]
    if any(w in title for w in urgent_words):
        urgency += 70
    else:
        urgency += 35

    # RISK keywords
    risky_words = ["no title", "salvage", "rebuilt", "as-is", "scam", "no paperwork", "stolen"]
    if any(w in title for w in risky_words):
        risk += 70
    else:
        risk += 25

    # Location boost
    if any(city in location for city in ["winnipeg", "toronto", "vancouver", "calgary", "edmonton", "miami", "phoenix", "dallas"]):
        profit += 5

    profit = max(0, min(100, profit))
    urgency = max(0, min(100, urgency))
    risk = max(0, min(100, risk))

    ai_score = max(0, min(100, (profit * 0.5) + (urgency * 0.4) - (risk * 0.3)))

    return {
        "profit_score": round(profit, 2),
        "urgency_score": round(urgency, 2),
        "risk_score": round(risk, 2),
        "ai_score": round(ai_score, 2),
    }

def passes_money_filter(scores: Dict[str, float]) -> bool:
    return (
        scores["profit_score"] >= MIN_PROFIT and
        scores["urgency_score"] >= MIN_URGENCY and
        scores["risk_score"] <= MAX_RISK and
        scores["ai_score"] >= MIN_AI_SCORE
    )
