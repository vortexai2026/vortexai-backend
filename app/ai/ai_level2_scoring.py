from __future__ import annotations

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.config.settings import settings

from app.services.valuation.market import market_tag
from app.services.valuation.comps_provider import get_comps, CompsError
from app.services.valuation.repair_estimator import estimate_repairs
from app.services.valuation.arv_engine import (
    calculate_arv,
    calculate_mao,
    calculate_spread,
)
from app.services.valuation.confidence_score import calculate_confidence


async def score_and_enrich_deal(db: AsyncSession, deal: Deal) -> Deal:
    """
    Hardened scoring logic with safety guardrails.
    """

    # -------------------------
    # 1️⃣ Market tagging
    # -------------------------
    tag = market_tag(deal.city, deal.state)
    deal.market_tag = tag

    if tag not in settings.MARKETS:
        deal.profit_flag = "red"
        await db.commit()
        await db.refresh(deal)
        return deal

    # -------------------------
    # 2️⃣ Repairs estimate
    # -------------------------
    repairs = estimate_repairs(
        year_built=deal.year_built,
        sqft=deal.sqft,
        distress_keywords=deal.notes,
    )

    # -------------------------
    # 3️⃣ Pull comps from provider
    # -------------------------
    arv = None
    comps_count = 0
    comps_payload = {}

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
        arv = None

    # -------------------------
    # 4️⃣ Minimum comps rule
    # -------------------------
    if comps_count < 3:
        deal.profit_flag = "red"
        deal.arv_estimated = None
        await db.commit()
        await db.refresh(deal)
        return deal

    # -------------------------
    # 5️⃣ ARV sanity guardrails
    # -------------------------
    seller_price = float(deal.seller_price or 0)

    if arv and seller_price:

        # Ratio protection
        ratio = arv / seller_price

        # If ARV more than 3x asking → reject
        if ratio > 3:
            arv = None

        # Stronger realistic cap
        if ratio > 2.5:
            arv = None

        # Absolute cap protection (customizable)
        if arv and arv > 1_500_000:
            arv = None

    # If ARV invalid → reject
    if not arv or not seller_price:
        deal.profit_flag = "red"
        deal.arv_estimated = None
        deal.repair_estimate = repairs
        await db.commit()
        await db.refresh(deal)
        return deal

    # -------------------------
    # 6️⃣ Calculate MAO & Spread
    # -------------------------
    mao = calculate_mao(arv, repairs)
    spread = calculate_spread(arv, repairs, seller_price)

    # -------------------------
    # 7️⃣ Confidence score
    # -------------------------
    confidence = calculate_confidence(
        comps_count=comps_count,
        has_address=bool(deal.address),
        has_sqft=bool(deal.sqft),
        has_beds_baths=bool(deal.beds and deal.baths),
    )

    # -------------------------
    # 8️⃣ Profit flag logic
    # -------------------------
    flag = "red"

    if spread >= settings.GREEN_MIN_SPREAD and confidence >= settings.MIN_CONFIDENCE_GREEN:
        flag = "green"
    elif spread >= settings.ORANGE_MIN_SPREAD:
        flag = "orange"

    # -------------------------
    # 9️⃣ Save everything
    # -------------------------
    deal.arv_estimated = float(arv)
    deal.repair_estimate = float(repairs)
    deal.mao = float(mao)
    deal.spread = float(spread)
    deal.confidence_score = int(confidence)
    deal.profit_flag = flag

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
    Find deals that haven't been scored yet.
    """

    q = select(Deal).where(
        (Deal.profit_flag == None) | (Deal.profit_flag == "")
    ).limit(limit)

    result = await db.execute(q)
    deals = list(result.scalars().all())

    processed = []

    for deal in deals:
        processed.append(await score_and_enrich_deal(db, deal))

    return processed
