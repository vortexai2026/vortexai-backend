# app/services/ingest_engine.py

from __future__ import annotations

from typing import Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal


async def ingest_one(
    db: AsyncSession,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Insert a single deal safely.
    Requires external_id for strong deduplication.
    """

    external_id = payload.get("external_id")
    title = str(payload.get("title", "")).strip()
    asset_type = str(payload.get("asset_type", "")).strip()
    city = str(payload.get("city", "")).strip()
    price = float(payload.get("price") or 0)

    # 🔒 Validate required fields
    if not external_id or not title or not asset_type or not city or price <= 0:
        return {
            "ok": False,
            "error": "Missing required fields: external_id, title, asset_type, city, price",
        }

    # 🔎 Strong duplicate check using external_id
    existing = await db.scalar(
        select(Deal).where(Deal.external_id == external_id)
    )

    if existing:
        return {
            "ok": True,
            "created": False,
            "deal_id": existing.id,
            "status": existing.status,
        }

    # ✅ Create new deal
    deal = Deal(
        external_id=external_id,
        title=title,
        asset_type=asset_type,
        city=city,
        price=price,
        score=float(payload.get("score") or 0.0),
        arv=payload.get("arv"),
        repairs=payload.get("repairs"),
        expected_profit=payload.get("expected_profit"),
        assignment_fee=payload.get("assignment_fee"),
        actual_profit=payload.get("actual_profit"),
        status="new",
    )

    db.add(deal)
    await db.flush()  # assign ID before commit

    return {
        "ok": True,
        "created": True,
        "deal_id": deal.id,
        "status": deal.status,
    }


async def ingest_batch(
    db: AsyncSession,
    deals: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Batch ingestion with safe commit.
    """

    created_count = 0
    deduped_count = 0
    failed_count = 0
    results = []

    for payload in deals:
        result = await ingest_one(db, payload)
        results.append(result)

        if not result.get("ok"):
            failed_count += 1
        elif result.get("created"):
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
