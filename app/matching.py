from typing import List, Tuple
from app.models import Buyer, Deal


def score_deal_for_buyer(buyer: Buyer, deal: Deal) -> float:
    """
    Simple scoring:
    + city match
    + asset type match
    + price within budget
    + more profit potential (if arv/repairs exist)
    """
    score = 0.0

    if buyer.asset_type and deal.asset_type and buyer.asset_type == deal.asset_type:
        score += 30

    if buyer.city and deal.city and buyer.city.lower().strip() == deal.city.lower().strip():
        score += 25

    if deal.price >= buyer.min_budget and deal.price <= buyer.max_budget:
        score += 30
    else:
        # penalize if outside budget
        score -= 20

    if deal.arv is not None and deal.repairs is not None:
        profit = deal.arv - deal.repairs - deal.price
        # Normalize a bit
        score += max(min(profit / 1000.0, 30), -30)

    return float(score)


def rank_deals(buyer: Buyer, deals: List[Deal]) -> List[Tuple[Deal, float]]:
    scored = [(d, score_deal_for_buyer(buyer, d)) for d in deals]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
