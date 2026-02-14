# app/services/ai_scoring.py

from __future__ import annotations
from typing import Tuple, Optional

from app.models.deal import Deal


def _safe_float(x) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def compute_expected_profit(deal: Deal) -> Optional[float]:
    """
    expected_profit = arv - price - repairs - assignment_fee
    (only if we have enough fields)
    """
    arv = _safe_float(getattr(deal, "arv", None))
    price = _safe_float(getattr(deal, "price", None))
    repairs = _safe_float(getattr(deal, "repairs", None)) or 0.0
    fee = _safe_float(getattr(deal, "assignment_fee", None)) or 0.0

    if arv is None or price is None:
        return None

    return float(arv - price - repairs - fee)


def score_deal(deal: Deal) -> Tuple[float, str]:
    """
    Returns (score 0-100, ai_decision)
    Decision:
      - ignore      (score < 40)
      - review      (40-69)
      - match_buyer (>= 70)
    """

    price = _safe_float(getattr(deal, "price", None)) or 0.0
    expected_profit = compute_expected_profit(deal)

    # Base score
    score = 50.0

    # Profit-based scoring (best signal)
    if expected_profit is not None:
        # Profit margin relative to price
        margin = expected_profit / max(price, 1.0)

        # Map margin to score bumps
        # 0% -> +0, 10% -> +10, 20% -> +20, 30% -> +30 (capped)
        score += max(0.0, min(40.0, margin * 100.0))

        # Big penalty if negative profit
        if expected_profit < 0:
            score -= 40.0
    else:
        # If we don't know profit yet, keep it "meh"
        score -= 10.0

    # Small sanity adjustments
    if price <= 0:
        score = 0.0

    # Clamp
    score = max(0.0, min(100.0, score))

    # Decision
    if score >= 70.0:
        decision = "match_buyer"
    elif score >= 40.0:
        decision = "review"
    else:
        decision = "ignore"

    return score, decision
