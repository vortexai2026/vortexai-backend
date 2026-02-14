from typing import List, Tuple
from app.models import Buyer, Deal


def calculate_profit_score(deal: Deal) -> float:
    if deal.arv and deal.repairs:
        profit = deal.arv - deal.repairs - deal.price
        return max(min(profit / 1000, 100), 0)
    return 20


def calculate_urgency_score(deal: Deal) -> float:
    if deal.source and "facebook" in deal.source.lower():
        return 70
    return 40


def calculate_risk_score(deal: Deal) -> float:
    if not deal.arv or not deal.repairs:
        return 60
    return 30


def score_deal_for_buyer(buyer: Buyer, deal: Deal) -> float:
    score = 0

    if buyer.asset_type == deal.asset_type:
        score += 30

    if buyer.city and deal.city and buyer.city.lower() == deal.city.lower():
        score += 25

    if buyer.min_budget <= deal.price <= buyer.max_budget:
        score += 30
    else:
        score -= 20

    score += calculate_profit_score(deal)

    return float(score)


def rank_deals(buyer: Buyer, deals: List[Deal]) -> List[Tuple[Deal, float]]:
    scored = [(d, score_deal_for_buyer(buyer, d)) for d in deals]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
