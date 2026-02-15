# app/services/negotiation_engine.py

from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.seller_call import SellerCall


@dataclass
class NegotiationOutput:
    recommended_offer: float
    max_offer: float
    strategy: str
    script: str
    reasoning: str


def _safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _calc_mao(arv: float, repairs: float, assignment_fee: float = 15000.0) -> float:
    # (ARV * 0.70) - repairs - assignment
    return max(0.0, (arv * 0.70) - repairs - assignment_fee)


def _offer_bands(mao: float):
    """
    Creates reasonable offer bands for
