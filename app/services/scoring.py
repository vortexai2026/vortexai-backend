# app/services/scoring.py
from typing import Tuple

def estimate_repairs(year_built: int | None, square_feet: int | None) -> float:
    """
    Simple repair estimator (placeholder).
    You will upgrade later with comps + condition + photos.
    """
    sf = square_feet or 0

    if not year_built:
        return max(25000.0, sf * 10.0)

    age = 2026 - year_built

    if age < 20:
        return max(15000.0, sf * 6.0)
    elif age < 50:
        return max(25000.0, sf * 12.0)
    else:
        return max(35000.0, sf * 18.0)

def compute_score(seller_price: float | None, arv: float | None, repairs: float) -> Tuple[str, float, float]:
    """
    Returns: (flag, spread, mao)
    """
    if not seller_price or not arv:
        return "red", 0.0, 0.0

    mao = (arv * 0.70) - repairs
    spread = mao - seller_price

    if spread >= 20000:
        return "green", spread, mao
    elif spread >= 5000:
        return "orange", spread, mao
    else:
        return "red", spread, mao

def score_deal(deal) -> None:
    """
    Mutates deal object (sets repair_estimate, mao, spread, profit_flag).
    """
    repairs = estimate_repairs(deal.year_built, deal.square_feet)

    flag, spread, mao = compute_score(
        seller_price=deal.seller_price,
        arv=deal.arv_estimated,
        repairs=repairs,
    )

    deal.repair_estimate = repairs
    deal.mao = mao
    deal.spread = spread
    deal.profit_flag = flag
