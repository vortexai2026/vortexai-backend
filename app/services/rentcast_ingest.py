# app/services/rentcast_ingest.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.markets import MARKETS
from app.models.deal import Deal
from app.services.rentcast_client import fetch_listings_for_city
from app.services.scoring import score_deal

def _safe_float(v):
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None

def _guess_arv(item: dict, price: float | None) -> float | None:
    """
    Temporary ARV logic to let the engine produce greens.
    Upgrade later with comps engine.
    """
    # try common fields that may exist
    for k in ["estimatedValue", "avm", "avmValue", "marketValue", "priceEstimate"]:
        if k in item and item.get(k):
            return _safe_float(item.get(k))

    if price:
        return float(price) * 1.15  # TEMP: +15% above list to test scoring
    return None

async def pull_deals(db: AsyncSession, limit_per_market: int = 50) -> dict:
    """
    Level 7 Pull:
    - Pull listings per configured market
    - Create Deal rows
    - Score each deal
    """
    created = 0
    markets_hit = 0

    for m in MARKETS:
        city = m["city"]
        state = m["state"]
        tag = m["tag"]

        listings = await fetch_listings_for_city(city=city, state=state, limit=limit_per_market)
        markets_hit += 1

        for item in listings:
            price = _safe_float(item.get("price"))
            arv = _guess_arv(item, price)

            deal = Deal(
                address=item.get("formattedAddress") or item.get("address"),
                city=item.get("city") or city,
                state=item.get("state") or state,
                zip_code=item.get("zipCode") or item.get("zip"),
                market_tag=tag,
                seller_price=price,
                arv_estimated=arv,
                square_feet=item.get("squareFootage"),
                year_built=item.get("yearBuilt"),
                beds=item.get("bedrooms"),
                baths=_safe_float(item.get("bathrooms")),
            )

            score_deal(deal)  # sets green/orange/red
            db.add(deal)
            created += 1

    await db.commit()

    return {
        "markets_hit": markets_hit,
        "created": created,
        "limit_per_market": limit_per_market,
    }
