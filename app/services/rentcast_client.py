# app/services/rentcast_client.py
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

import httpx

RENTCAST_BASE_URL = os.getenv("RENTCAST_BASE_URL", "https://api.rentcast.io/v1")
RENTCAST_API_KEY = os.getenv("RENTCAST_API_KEY", "")

class RentcastError(RuntimeError):
    pass

def _auth_headers() -> Dict[str, str]:
    if not RENTCAST_API_KEY:
        raise RentcastError("RENTCAST_API_KEY is not set")
    # RentCast uses an API key header. If your account uses a different header name,
    # adjust it here.
    return {
        "X-Api-Key": RENTCAST_API_KEY,
        "Accept": "application/json",
    }

async def fetch_listings_for_city(
    city: str,
    state: str,
    *,
    status: str = "forSale",
    limit: int = 50,
    offset: int = 0,
    property_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch listings for a given city/state from RentCast.

    NOTE:
    - The exact endpoint/params can differ by RentCast plan/API version.
    - If you already know the correct endpoint you’re using, keep the signature
      and adjust the URL/params below.
    """
    params: Dict[str, Union[str, int]] = {
        "city": city,
        "state": state,
        "limit": limit,
        "offset": offset,
        "status": status,
    }
    if property_type:
        params["propertyType"] = property_type
    if min_price is not None:
        params["minPrice"] = int(min_price)
    if max_price is not None:
        params["maxPrice"] = int(max_price)

    # Common pattern is /listings or /properties/listings depending on version.
    # Keep this as /listings first; if your API differs, change ONLY this path.
    url = f"{RENTCAST_BASE_URL}/listings"

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=_auth_headers(), params=params)

    if r.status_code == 401:
        raise RentcastError("RentCast unauthorized (check RENTCAST_API_KEY)")
    if r.status_code >= 400:
        raise RentcastError(f"RentCast error {r.status_code}: {r.text[:500]}")

    data = r.json()

    # Some APIs return {"listings":[...]} others return a raw list.
    if isinstance(data, dict) and "listings" in data and isinstance(data["listings"], list):
        return data["listings"]
    if isinstance(data, list):
        return data

    # Fallback: return empty list rather than crashing ingestion
    return []
