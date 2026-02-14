# app/services/ingest_engine.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal


def _norm(s: str) -> str:
    return (s or "").strip().lower()


async def _find_duplicate(
    db: AsyncSession,
    title: str,
    asset_type: str,
    city: str,
    price: float,
) -> Deal | None:
    """
    Dedupe strategy (no schema changes):
    - same title + city + asset_type + price
    - within last 30 days
    """
    since = datetime.now(timezone.utc) - timedelta(days=30)

    q = (
        select(Deal)
        .where(
            and_(
                Deal.price == float(price),
                Deal.city == city,
                Deal.asset_type == asset_type,
                Deal.title == title,
                Deal.created_at >= since,
            )
        )
        .order_by(Deal.created_at.desc())
        .limit(1)
    )
    return await db.scalar(q)


async def ingest_one(db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    title = str(payload.get("title", "")).strip()
    asset_type = str(payload.get("asset_type", "")).strip()
    city = str(payload.get("city", "")).strip()
    price = float(payload.get("price") or 0)

    if not title or not asset_type or not city or price <= 0:
        return {"ok": False, "error": "Missing required fields: title, asset_type, city, price"}

    # Normalize lightly (helps dedupe)
    title_n = " ".join(title.split())
    asset_type_n = " ".join(asset_type.split())
    city_n = " ".join(city.split())

    dup = await _find_duplicate(db, title_n, asset_type_n, city_n, price)
    if dup:
        return {"ok": True, "created": False, "deal_id": dup.id, "status": getattr(dup, "status", None)}

    deal = Deal(
        title=title_n,
        asset_type=asset_type_n,
        city=city_n,
        price=price,
        score=float(payload.get("score") or 0.0),
    )

    # optional fields if your Deal model has them
    if hasattr(deal, "arv"):
        deal.arv = payload.get("arv")
    if hasattr(deal, "repairs"):
        deal.repairs = payload.get("repairs")
    if hasattr(deal, "assignment_fee"):
        deal.assignment_fee = payload.get("assignment_fee")

    # make sure worker picks it up
    if hasattr(deal, "status"):
        deal.status = "new"

    db.add(deal)
    await db.flush()  # assign id without committing yet

    return {"ok": True, "created": True, "deal_id": deal.id, "status": getattr(deal, "status", None)}


async def ingest_batch(db: AsyncSession, deals: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    created_count = 0
    deduped_count = 0
    failed_count = 0

    for d in deals:
        r = await ingest_one(db, d)
        results.append(r)

        if not r.get("ok"):
            failed_count += 1
        elif r.get("created"):
            created_count += 1
        else:
            deduped_count += 1

    await db.commit()

    return {
        "ok": True,
        "created": created_count,
        "deduped": deduped_count,
        "failed": failed_count,
        "results": results,
    }
