from typing import Dict
from app.config.money_rules import DEAL_TYPES

def score_deal(deal: Dict) -> Dict:
    price = float(deal.get("price", 0))
    title = (deal.get("title") or "").lower()
    asset_type = deal.get("asset_type")

    profit = urgency = risk = 0

    rules = DEAL_TYPES.get(asset_type)
    if not rules:
        return {"profit": 0, "urgency": 0, "risk": 100, "ai_score": 0}

    if rules["min_price"] <= price <= rules["max_price"]:
        profit += 60
    else:
        risk += 40

    if any(k in title for k in rules["keywords"]):
        urgency += 60
    else:
        urgency += 20

    if "scam" in title or "no title" in title:
        risk += 60
    else:
        risk += 20

    ai_score = max(0, min(100, profit + urgency - risk))

    return {
        "profit": profit,
        "urgency": urgency,
        "risk": risk,
        "ai_score": ai_score
    }
