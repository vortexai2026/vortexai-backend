from __future__ import annotations

import math
from typing import Tuple
from app.models.deal import Deal

GREEN_MIN_SPREAD = float(25000)
ORANGE_MIN_SPREAD = float(10000)
MIN_CONFIDENCE_GREEN = int(80)

def market_tag(city: str | None, state: str | None) -> str:
    city = (city or "").lower()
    state = (state or "").upper()

    # For now: Dallas = TX_DFW
    if state == "TX" and "dallas" in city:
        return "TX_DFW"
    return f"{state}_{(city or 'UNKNOWN').upper()}"

def estimate_repairs(deal: Deal) -> float:
    # Very simple v1 estimator
    base = 25000.0
    if deal.year_built and deal.year_built < 1980:
        base += 10000.0
    if deal.sqft and deal.sqft > 1800:
        base += 7000.0
    if deal.notes and any(k in deal.notes.lower() for k in ["foundation", "roof", "fire", "water", "mold"]):
        base += 15000.0
    return float(base)

def calculate_mao(arv: float, repairs: float) -> float:
    # 70% rule
    return float((arv * 0.70) - repairs)

def calculate_spread(mao: float, seller_price: float) -> float:
    return float(mao - seller_price)

def confidence_score_stub(deal: Deal) -> int:
    # Simple confidence: we can improve later
    score = 70
    if deal.address: score += 10
    if deal.sqft: score += 10
    if deal.beds and deal.baths: score += 5
    return min(95, score)

def arv_stub(deal: Deal) -> float | None:
    """
    TEMPORARY ARV logic:
    Replace this with RentCast comps/AVM later.
    """
    if not deal.sqft:
        return None
    # rough $/sqft assumption for Dallas v1
    ppsf = 250.0
    return float(deal.sqft * ppsf)

def apply_guardrails(arv: float | None, seller_price: float | None) -> float | None:
    if not arv or not seller_price or seller_price <= 0:
        return None
    ratio = arv / seller_price
    # If ARV is unrealistic compared to ask, reject
    if ratio > 3.0:
        return None
    if ratio > 2.5:
        return None
    if arv > 1_500_000:
        return None
    return arv

def score_deal(deal: Deal) -> Deal:
    deal.market_tag = market_tag(deal.city, deal.state)

    repairs = estimate_repairs(deal)
    seller_price = float(deal.seller_price or 0)

    arv = arv_stub(deal)
    arv = apply_guardrails(arv, seller_price)

    if not arv or seller_price <= 0:
        deal.profit_flag = "red"
        deal.repair_estimate = float(repairs)
        deal.arv_estimated = None
        deal.mao = None
        deal.spread = None
        deal.confidence_score = confidence_score_stub(deal)
        return deal

    mao = calculate_mao(arv, repairs)
    spread = calculate_spread(mao, seller_price)
    conf = confidence_score_stub(deal)

    # Flag logic
    flag = "red"
    if spread >= GREEN_MIN_SPREAD and conf >= MIN_CONFIDENCE_GREEN:
        flag = "green"
    elif spread >= ORANGE_MIN_SPREAD:
        flag = "orange"

    deal.arv_estimated = float(arv)
    deal.repair_estimate = float(repairs)
    deal.mao = float(mao)
    deal.spread = float(spread)
    deal.confidence_score = int(conf)
    deal.profit_flag = flag

    return deal
