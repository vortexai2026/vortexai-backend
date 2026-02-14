# app/services/ai_scoring.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer import Buyer
from app.models.deal import Deal


@dataclass
class ScoreResult:
    ai_score: float
    profit_score: float
    risk_score: float
    demand_score: float
    liquidity_score: float
    urgency_score: float
    confidence: float
    decision: str  # match_buyer | review | reject


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def _safe_float(x: Optional[float], default: float = 0.0) -> float:
    try:
        return float(x) if x is not None else default
    except Exception:
        return default


async def score_deal(db: AsyncSession, deal: Deal) -> ScoreResult:
    """
    Real scoring (still deterministic & fast):
    - Profit score: expected_profit, assignment_fee bonus
    - Risk score: repairs/arv ratio, missing data penalty
    - Demand score: count of matching buyers (same city/asset_type & budget >= price)
    - Liquidity score: how far below average budget this deal is
    - Urgency score: older deals get a slight urgency bump
    Produces: ai_score (0-100), confidence (0-100), decision
    """

    price = _safe_float(deal.price)
    arv = _safe_float(getattr(deal, "arv", None))
    repairs = _safe_float(getattr(deal, "repairs", None))
    assignment_fee = _safe_float(getattr(deal, "assignment_fee", None))
    expected_profit = _safe_float(getattr(deal, "expected_profit", None))

    # If expected_profit not computed yet, compute a best-effort
    if expected_profit == 0.0 and arv > 0 and price > 0:
        expected_profit = arv - price - repairs

    # -------------------------
    # 1) Demand Score (buyers)
    # -------------------------
    buyer_count = await db.scalar(
        select(func.count())
        .select_from(Buyer)
        .where(
            Buyer.asset_type == deal.asset_type,
            Buyer.city == deal.city,
            Buyer.max_budget >= price,
            Buyer.is_active == True,
        )
    )
    buyer_count = int(buyer_count or 0)
    # 0 buyers => 0, 1 => 40, 3 => 70, 5+ => 90
    if buyer_count <= 0:
        demand_score = 0.0
    elif buyer_count == 1:
        demand_score = 40.0
    elif buyer_count <= 3:
        demand_score = 70.0
    elif buyer_count <= 5:
        demand_score = 85.0
    else:
        demand_score = 90.0

    # Avg budget for matching buyers (liquidity)
    avg_budget = await db.scalar(
        select(func.avg(Buyer.max_budget))
        .where(
            Buyer.asset_type == deal.asset_type,
            Buyer.city == deal.city,
            Buyer.is_active == True,
        )
    )
    avg_budget = _safe_float(avg_budget, default=0.0)

    # -------------------------
    # 2) Liquidity Score
    # -------------------------
    # If deal price is far below avg budget => easier to move
    if avg_budget <= 0 or price <= 0:
        liquidity_score = 40.0
    else:
        ratio = price / max(avg_budget, 1.0)  # lower is better
        # ratio 0.4 => 95, 0.6 => 85, 0.8 => 70, 1.0 => 55, 1.2 => 40
        liquidity_score = _clamp(110 - (ratio * 55), 20, 95)

    # -------------------------
    # 3) Risk Score
    # -------------------------
    # Higher repairs/arv ratio => higher risk => lower score
    data_penalty = 0.0
    if arv <= 0:
        data_penalty += 20.0
    if price <= 0:
        data_penalty += 10.0

    if arv > 0 and repairs >= 0:
        repair_ratio = repairs / max(arv, 1.0)  # 0.10 good, 0.30 risky
        # 0.05 => 95, 0.10 => 85, 0.20 => 70, 0.30 => 55, 0.40 => 40
        base_risk = _clamp(100 - (repair_ratio * 150), 25, 95)
    else:
        base_risk = 50.0

    risk_score = _clamp(base_risk - data_penalty, 0, 95)

    # -------------------------
    # 4) Profit Score
    # -------------------------
    # Scale expected profit into 0-100
    # 0 => 10, 5k => 40, 10k => 60, 20k => 80, 30k => 92, 50k => 98
    if expected_profit <= 0:
        profit_score = 10.0
    elif expected_profit < 5000:
        profit_score = 25.0
    elif expected_profit < 10000:
        profit_score = 45.0
    elif expected_profit < 20000:
        profit_score = 70.0
    elif expected_profit < 30000:
        profit_score = 85.0
    elif expected_profit < 50000:
        profit_score = 94.0
    else:
        profit_score = 98.0

    # assignment fee bonus (if you use it)
    if assignment_fee > 0:
        profit_score = _clamp(profit_score + 3.0, 0, 100)

    # -------------------------
    # 5) Urgency Score
    # -------------------------
    created_at = getattr(deal, "created_at", None)
    if isinstance(created_at, datetime):
        age_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600.0
    else:
        age_hours = 0.0
    # slight bump as deals age (0h => 40, 24h => 55, 72h => 70, 168h => 85)
    urgency_score = _clamp(40 + (age_hours / 168.0) * 45.0, 40, 85)

    # -------------------------
    # 6) Weighted AI Score
    # -------------------------
    # Weighting tuned for marketplace:
    # Profit 35%, Risk 20%, Demand 20%, Liquidity 15%, Urgency 10%
    ai_score = (
        profit_score * 0.35
        + risk_score * 0.20
        + demand_score * 0.20
        + liquidity_score * 0.15
        + urgency_score * 0.10
    )
    ai_score = _clamp(ai_score, 0, 100)

    # -------------------------
    # 7) Confidence
    # -------------------------
    # Confidence depends on how complete the deal is + buyer demand
    completeness = 100.0
    if arv <= 0:
        completeness -= 30.0
    if repairs <= 0:
        completeness -= 10.0
    if price <= 0:
        completeness -= 30.0
    if not deal.city:
        completeness -= 10.0
    if not deal.asset_type:
        completeness -= 10.0
    completeness = _clamp(completeness, 0, 100)

    demand_conf = _clamp(30 + buyer_count * 12, 30, 90)
    confidence = _clamp((completeness * 0.65) + (demand_conf * 0.35), 0, 100)

    # -------------------------
    # 8) Decision
    # -------------------------
    # Require both score and demand for auto-match
    if ai_score >= 78 and buyer_count >= 1 and profit_score >= 60:
        decision = "match_buyer"
    elif ai_score >= 55:
        decision = "review"
    else:
        decision = "reject"

    return ScoreResult(
        ai_score=float(ai_score),
        profit_score=float(profit_score),
        risk_score=float(risk_score),
        demand_score=float(demand_score),
        liquidity_score=float(liquidity_score),
        urgency_score=float(urgency_score),
        confidence=float(confidence),
        decision=decision,
    )
