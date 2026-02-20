from __future__ import annotations

import httpx
from app.config.settings import settings

class CompsError(Exception):
    pass

async def get_comps(
    *,
    address: str | None,
    city: str,
    state: str,
    zip_code: str | None,
    beds: int | None,
    baths: float | None,
    sqft: int | None,
) -> dict:
    """
    Returns normalized comps payload:
    {
      "median_price": float | None,
      "avg_price": float | None,
      "comps_count": int,
      "raw": dict
    }
    """
    provider = settings.PROPERTY_PROVIDER.lower().strip()

    if provider == "rentcast":
        return await _rentcast_value_estimate(
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            beds=beds,
            baths=baths,
            sqft=sqft,
        )

    raise CompsError(f"Unsupported PROPERTY_PROVIDER={settings.PROPERTY_PROVIDER}")

async def _rentcast_value_estimate(
    *,
    address: str | None,
    city: str,
    state: str,
    zip_code: str | None,
    beds: int | None,
    baths: float | None,
    sqft: int | None,
) -> dict:
    """
    RentCast has endpoints for value estimates. Exact params can vary by plan.
    This version is a practical starter that works for many setups.
    If your RentCast plan uses different endpoint/params, update here only.
    """
    if not settings.RENTCAST_API_KEY:
        raise CompsError("Missing RENTCAST_API_KEY env var")

    # Starter endpoint (common): /v1/avm/value
    # NOTE: If your account uses a different path, adjust URL here.
    url = "https://api.rentcast.io/v1/avm/value"

    params: dict = {
        "city": city,
        "state": state,
    }
    if zip_code:
        params["zipCode"] = zip_code
    if address:
        params["address"] = address
    if beds is not None:
        params["beds"] = beds
    if baths is not None:
        params["baths"] = baths
    if sqft is not None:
        params["squareFeet"] = sqft

    headers = {
        "X-Api-Key": settings.RENTCAST_API_KEY,
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params, headers=headers)

    if r.status_code >= 400:
        raise CompsError(f"RentCast error {r.status_code}: {r.text[:300]}")

    data = r.json()

    # Try to normalize common shapes
    # Some responses include "price" or "value"; others include "avm" object.
    price = None
    for key in ("price", "value", "estimatedValue"):
        if isinstance(data.get(key), (int, float)):
            price = float(data[key])
            break

    if price is None and isinstance(data.get("avm"), dict):
        avm = data["avm"]
        for key in ("value", "price", "estimatedValue"):
            if isinstance(avm.get(key), (int, float)):
                price = float(avm[key])
                break

    # Comps count might be available
    comps_count = 0
    if isinstance(data.get("comparables"), list):
        comps_count = len(data["comparables"])
    elif isinstance(data.get("comps"), list):
        comps_count = len(data["comps"])

    # Use price as median/avg when only one estimate is returned
    median_price = price
    avg_price = price

    return {
        "median_price": median_price,
        "avg_price": avg_price,
        "comps_count": comps_count,
        "raw": data,
    }
