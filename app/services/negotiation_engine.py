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
    Creates reasonable offer bands for negotiation:
    - opener: 85% of mao (room to move)
    - target: 95% of mao
    - max: 100% of mao
    """
    opener = round(mao * 0.85, 0)
    target = round(mao * 0.95, 0)
    max_offer = round(mao, 0)
    return opener, target, max_offer


def _motivation_multiplier(motivation_level: int | None):
    """
    Higher motivation => can push lower.
    Lower motivation => must be closer to mao.
    """
    if motivation_level is None:
        return 1.0
    m = max(1, min(5, int(motivation_level)))
    # 5 => 0.92 (more aggressive)
    # 1 => 1.02 (less aggressive)
    return {
        5: 0.92,
        4: 0.95,
        3: 0.98,
        2: 1.00,
        1: 1.02
    }[m]


def _build_script(city: str, opener: float, target: float, max_offer: float, timeline: str | None):
    tl = timeline or "this month"
    return f"""SELLER SCRIPT (Vortex)

1) Set frame:
"Thanks again for your time. I buy properties as-is and close fast if the numbers work."

2) Confirm pain + timeline:
"You mentioned your timeline is {tl}. If we could close on your schedule, what would be most important to you — speed, certainty, or price?"

3) Present offer (opener):
"Based on repairs and closing costs, the best I can do is around ${int(opener):,}. I can do as-is, no inspections, and we cover normal closing steps."

4) If they push back:
"I hear you. If we can solve the speed/certainty part for you, is there any flexibility from your asking price?"

5) Counter ladder:
"If you can meet me at ${int(target):,}, I can push this forward right away.
My absolute top number is ${int(max_offer):,} — and that’s only if the property condition matches what you described."

6) Close:
"If we agree today, I can send a simple agreement and we start title immediately. Does that work for you?"
"""


async def generate_negotiation_plan(db: AsyncSession, deal_id: int, assignment_fee: float = 15000.0) -> NegotiationOutput:
    # Load deal
    deal_res = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = deal_res.scalar_one_or_none()
    if not deal:
        raise ValueError("Deal not found")

    arv = _safe_float(getattr(deal, "arv", None), 0.0)
    repairs = _safe_float(getattr(deal, "repairs", None), 0.0)

    # Load latest seller call
    call_q = (
        select(SellerCall)
        .where(SellerCall.deal_id == deal.id)
        .order_by(SellerCall.call_date.desc())
        .limit(1)
    )
    call_res = await db.execute(call_q)
    last_call = call_res.scalar_one_or_none()

    motivation = int(last_call.motivation_level) if (last_call and last_call.motivation_level is not None) else None
    asking = _safe_float(last_call.asking_price if last_call else None, 0.0)
    timeline = (last_call.timeline if last_call else None)

    mao = _calc_mao(arv, repairs, assignment_fee=assignment_fee)

    opener, target, max_offer = _offer_bands(mao)

    # Adjust recommended offer slightly based on motivation
    mult = _motivation_multiplier(motivation)
    recommended = round(target * mult, 0)

    # Ensure recommended doesn't exceed max
    if recommended > max_offer:
        recommended = max_offer

    # Strategy text
    strategy = "Speed + certainty leverage; anchor low; walk up with conditions."
    if motivation in (4, 5):
        strategy = "High motivation: anchor lower, trade speed for price, push fast close."
    elif motivation in (1, 2):
        strategy = "Low motivation: keep offer nearer to MAO, focus on convenience and certainty."

    # Reasoning summary
    reasoning = (
        f"ARV={arv:.0f}, Repairs={repairs:.0f}, AssignmentFee={assignment_fee:.0f}, "
        f"MAO={(mao):.0f}. Motivation={motivation or 'N/A'}, Asking={asking:.0f}. "
        f"Opener={opener:.0f}, Target={target:.0f}, Max={max_offer:.0f}, Recommended={recommended:.0f}."
    )

    city = (deal.city or "your market")
    script = _build_script(city, opener, target, max_offer, timeline)

    return NegotiationOutput(
        recommended_offer=float(recommended),
        max_offer=float(max_offer),
        strategy=strategy,
        script=script,
        reasoning=reasoning
    )
