# app/services/rentcast_client.py
import os
import httpx
from typing import Any, Dict, Optional

RENTCAST_API_KEY = os.getenv("RENTCAST_API_KEY")
RENTCAST_BASE_URL = os.getenv("RENTCAST_BASE_URL", "https://api.rentcast.io")

if not RENTCAST_API_KEY:
    # don't crash startup; crash only when used
    pass


class RentCastClient:
    def __init__(self) -> None:
        if not RENTCAST_API_KEY:
            raise ValueError("RENTCAST_API_KEY is missing")

        self.headers = {
            "accept": "application/json",
            "X-Api-Key": RENTCAST_API_KEY,
        }

    async def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{RENTCAST_BASE_URL.rstrip('/')}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers=self.headers, params=params or {})
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                return data
            # normalize
            return {"data": data}

    # -------------------------
    # IMPORTANT:
    # RentCast endpoints can vary by plan/version.
    # These functions are written to be easy to adjust.
    # -------------------------

    async def search_listings(self, city: str, state: str, limit: int = 50) -> Dict[str, Any]:
        """
        Try a generic listings search. If your RentCast plan uses a different endpoint,
        change only the 'path' and params here.
        """
        path = os.getenv("RENTCAST_LISTINGS_PATH", "/v1/listings/sale")
        params = {
            "city": city,
            "state": state,
            "limit": limit,
        }
        return await self.get_json(path, params=params)

    async def avm_value(self, address: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """
        AVM/valuation lookup for ARV estimate.
        """
        path = os.getenv("RENTCAST_AVM_PATH", "/v1/avm/value")
        params = {"address": address, "city": city, "state": state, "zip": zip_code}
        return await self.get_json(path, params=params)
