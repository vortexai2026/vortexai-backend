# app/services/rentcast_ingest.py
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.markets import MARKETS
from app.models.deal import Deal
from app.services.rentcast_client import RentCastClient
from app.services.scoring import estimate_repairs, compute_score


def _to_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _to_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        return int(float(x))
    except Exception:
        return None


async def upsert_deal_by_address(db: AsyncSession, payload: Dict[str, Any]) -> Deal:
    """
    Minimal dedupe: address + zip_code
    """
    address = payload.get("address")
    zip_code = payload.get("zip_code")

    q = select(Deal).where(Deal.address == address, Deal.zip_code == zip_code)
    res = await db.execute(q)
    existing = res.scalars().first()

    if existing:
        # update fields
        for k, v in payload.items():
            setattr(existing, k, v)
        await db.commit()
        await db.refresh(existing)
        return existing

    deal = Deal(**payload)
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


async def pull_market(db: AsyncSession, market_tag: str, per_city_limit: int = 25) -> int:
    """
    Pull listings from RentCast for the market's cities.
    Create/Update deals and compute score.
    """
    client = RentCastClient()
    market = MARKETS[market_tag]
    state = market["state"]
    cities: List[str] = market["cities"]

    created_or_updated = 0

    for city in cities:
        data = await client.search_listings(city=city, state=state, limit=per_city_limit)
        items = data.get("listings") or data.get("data") or []

        # items shape depends on endpoint; we normalize lightly
        if isinstance(items, dict):
            items = items.get("results", [])

        if not isinstance(items, list):
            continue

        for it in items:
            # try to map common listing fields
            address = it.get("address") or it.get("formattedAddress") or it.get("streetAddress")
            zip_code = it.get("zip") or it.get("zipCode") or it.get("postalCode")
            if not address or not zip_code:
                continue

            seller_price = _to_float(it.get("price") or it.get("listPrice"))
            beds = _to_int(it.get("beds") or it.get("bedrooms"))
            baths = _to_float(it.get("baths") or it.get("bathrooms"))
            sqft = _to_int(it.get("sqft") or it.get("livingArea"))
            year_built = _to_int(it.get("yearBuilt"))

            # ----- ARV via AVM -----
            arv_est = None
            try:
                avm = await client.avm_value(address=address, city=city, state=state, zip_code=str(zip_code))
                arv_est = _to_float(avm.get("price") or avm.get("value") or avm.get("avm"))
            except Exception:
                # allow ingestion even if AVM fails
                arv_est = None

            notes = (it.get("description") or "")[:500]
            repairs = estimate_repairs(sqft, notes)

            score = compute_score(seller_price=seller_price, arv=arv_est, repairs=repairs)

            deal_payload = {
                "address": address,
                "city": city,
                "state": state,
                "zip_code": str(zip_code),
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "year_built": year_built,
                "seller_price": seller_price,
                "notes": notes,
                "market_tag": market_tag,
                "arv_estimated": score.arv,
                "repair_estimate": score.repairs,
                "mao": score.mao,
                "spread": score.spread,
                "confidence_score": score.confidence,
                "profit_flag": score.flag,
                "status": "Lead",
            }

            await upsert_deal_by_address(db, deal_payload)
            created_or_updated += 1

    return created_or_updated


async def pull_all_markets(db: AsyncSession, total_target: int = 50) -> Dict[str, Any]:
    """
    Pull both markets; tries to approximate total_target by splitting.
    """
    per_market = max(10, total_target // max(1, len(MARKETS)))
    per_city_limit = max(5, per_market // 3)

    results = {}
    total = 0

    for tag in MARKETS.keys():
        n = await pull_market(db, tag, per_city_limit=per_city_limit)
        results[tag] = n
        total += n

    return {"pulled_total": total, "by_market": results}
