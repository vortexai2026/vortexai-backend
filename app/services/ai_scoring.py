from typing import Tuple, Optional
from app.models.deal import Deal


DISTRESS_KEYWORDS = [
    "foreclosure",
    "pre-foreclosure",
    "probate",
    "estate sale",
    "distressed",
    "handyman",
    "investor special",
    "fixer",
    "as-is",
    "motivated",
    "must sell",
    "bring all offers",
    "vacant",
    "fire damage",
    "water damage",
    "needs tlc",
    "cash only",
    "price reduced",
    "below market",
]


def contains_distress(text: str) -> bool:
    if not text:
        return False
    text = text.lower()
    return any(keyword in text for keyword in DISTRESS_KEYWORDS)


def compute_expected_profit(deal: Deal) -> Optional[float]:
    if not deal.arv or not deal.price:
        return None

    repairs = deal.repairs or 0
    fee = deal.assignment_fee or 0

    return float(deal.arv - deal.price - repairs - fee)


def score_deal(deal: Deal) -> Tuple[float, str]:

    if not deal.price or not deal.arv:
        return 0.0, "ignore"

    expected_profit = compute_expected_profit(deal)
    if expected_profit is None:
        return 0.0, "ignore"

    margin = expected_profit / max(deal.price, 1)

    # 70% Rule Check
    max_allowable_offer = (deal.arv * 0.70) - (deal.repairs or 0)
    passes_70_rule = deal.price <= max_allowable_offer

    # Distress detection
    distress_hit = contains_distress(deal.title)

    # HARD FILTERS
    if expected_profit < 30000:
        return 20.0, "ignore"

    if margin < 0.20:
        return 25.0, "ignore"

    if not passes_70_rule:
        return 30.0, "ignore"

    # If passes everything:
    score = 85.0

    if distress_hit:
        score += 10.0

    if margin >= 0.30:
        score += 5.0

    score = min(score, 100.0)

    return score, "match_buyer"
