from __future__ import annotations

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.deal import Deal

from app.services.valuation.market import market_tag
from app.services.valuation.comps_provider import get_comps, CompsError
from app.services.valuation.repair_estimator import estimate_repairs
from app.services.valuation.arv_engine import calculate_arv, calculate_mao, calculate_spread
from app.services.valuation.confidence_score import calculate_confidence

async def score_and_enrich_deal(db: AsyncSession, deal: Deal) -> Deal:
    """
    Enrich deal with:
    market_tag, arv_estimated, repairs, mao, spread, confidence_score, profit_flag
    """
    # 1) Market tag
    tag = market_tag(deal.city, deal.state)
    deal.market_tag = tag

    # If not in our 2 markets, mark as red & return (keeps system focused)
    if tag is None or tag not in settings.MARKETS:
        deal.profit_flag = "red"
        await db.commit()
        await db.refresh(deal)
        return deal

    # 2) Repairs (V1 heuristic)
    repairs = estimate_repairs(
        year_built=deal.year_built,
        sqft=deal.sqft,
        distress_keywords=deal.notes,
    )

    # 3) Comps / ARV
    comps_payload = {}
    arv = None
    comps_count = 0
    try:
        comps_payload = await get_comps(
            address=deal.address,
            city=deal.city or "",
            state=deal.state or "",
            zip_code=deal.zip_code,
            beds=deal.beds,
            baths=deal.baths,
            sqft=deal.sqft,
        )
        comps_count = int(comps_payload.get("comps_count") or 0)
        arv = calculate_arv(comps_payload)
    except CompsError:
        # If comps provider fails, we can't trust valuation
        arv = None

    # 4) Confidence
    conf = calculate_confidence(
        comps_count=comps_count,
        has_address=bool(deal.address),
        has_sqft=bool(deal.sqft),
        has_beds_baths=bool(deal.beds) and bool(deal.baths),
    )

    # 5) Spread + Flag
    seller_price = float(deal.seller_price or 0)
    flag = "red"
    mao = None
    spread = None

    if arv is not None and seller_price > 0:
        mao = calculate_mao(arv, repairs)
        spread = calculate_spread(arv, repairs, seller_price)

        if spread >= settings.GREEN_MIN_SPREAD and conf >= settings.MIN_CONFIDENCE_GREEN:
            flag = "green"
        elif spread >= settings.ORANGE_MIN_SPREAD:
            flag = "orange"
        else:
            flag = "red"
    else:
        # Missing price or ARV -> red until data is fixed
        flag = "red"

    # 6) Save
    deal.arv_estimated = float(arv) if arv is not None else None
    deal.repair_estimate = float(repairs)
    deal.mao = float(mao) if mao is not None else None
    deal.spread = float(spread) if spread is not None else None
    deal.confidence_score = int(conf)
    deal.profit_flag = flag

    # Store raw comps JSON if you want
    if comps_payload:
        try:
            deal.comps_raw = json.dumps(comps_payload.get("raw", comps_payload))[:20000]
        except Exception:
            deal.comps_raw = None

    await db.commit()
    await db.refresh(deal)
    return deal

async def score_pending_deals(db: AsyncSession, limit: int = 50) -> list[Deal]:
    """
    Find deals in our target markets that are not yet flagged and score them.
    """
    q = select(Deal).where(
        (Deal.profit_flag == None)  # noqa: E711
    ).order_by(Deal.created_at.desc()).limit(limit)

    res = await db.execute(q)
    deals = list(res.scalars().all())

    out: list[Deal] = []
    for d in deals:
        out.append(await score_and_enrich_deal(db, d))
    return out
