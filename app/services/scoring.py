# app/services/scoring.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScoreResult:
    arv: Optional[float]
    repairs: Optional[float]
    mao: Optional[float]
    spread: Optional[float]
    confidence: int
    flag: str  # green/orange/red


def estimate_repairs(sqft: Optional[int], notes: str = "") -> float:
    """
    Simple repair estimator. Upgrade later.
    """
    base = 25000.0
    if sqft and sqft > 1800:
        base += 10000.0
    if "foundation" in (notes or "").lower():
        base += 20000.0
    if "fire" in (notes or "").lower():
        base += 25000.0
    return float(base)


def compute_score(
    seller_price: Optional[float],
    arv: Optional[float],
    repairs: Optional[float],
    assignment_fee: float = 10000.0,
    rule_pct: float = 0.70,
) -> ScoreResult:
    if not seller_price or not arv:
        return ScoreResult(arv=arv, repairs=repairs, mao=None, spread=None, confidence=30, flag="red")

    repairs = repairs or 0.0
    mao = (arv * rule_pct) - repairs - assignment_fee
    spread = arv - seller_price - repairs

    # confidence: basic now; you can tie this to comps count later
    confidence = 70
    if seller_price < mao:
        confidence += 15
    if spread > 50000:
        confidence += 10
    confidence = max(1, min(99, confidence))

    # flag logic
    if seller_price <= mao and spread >= 50000:
        flag = "green"
    elif seller_price <= (mao * 1.10) and spread >= 25000:
        flag = "orange"
    else:
        flag = "red"

    return ScoreResult(arv=arv, repairs=repairs, mao=mao, spread=spread, confidence=confidence, flag=flag)
