import os
import math
from typing import Dict, Any, List, Optional
import httpx

from app.models.deal import Deal

def _provider() -> str:
    return os.getenv("COMPS_PROVIDER", "custom").lower()

def _median(vals: List[float]) -> Optional[float]:
    vals = [v for v in vals if v and v > 0]
    if not vals:
        return None
    vals.sort()
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid-1] + vals[mid]) / 2

def arv_from_comps(comps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Expects comps with fields: sale_price, sqft (optional)
    Returns: arv, confidence
    """
    prices = [float(c.get("sale_price") or 0) for c in comps]
    arv = _median(prices)
    n = len([p for p in prices if p > 0])
    confidence = min(0.95, 0.35 + (n * 0.12))  # simple ramp
    return {"arv": arv, "confidence": round(confidence, 2), "comp_count": n}

async def fetch_comps(deal: Deal) -> List[Dict[str, Any]]:
    """
    This is a provider plug-in. Implement one provider first.
    """
    p = _provider()
    if p == "rentcast":
        # Example placeholder — adjust to the exact endpoint you have.
        api_key = os.environ["RENTCAST_API_KEY"]
        base = "https://api.rentcast.io/v1"
        # You must map to their actual comps endpoint.
        url = f"{base}/avm/value"  # if your plan supports AVM; otherwise implement comps endpoint
        params = {"address": deal.address, "city": deal.city, "state": deal.state, "zip": deal.zip}
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, params=params, headers={"X-Api-Key": api_key})
            r.raise_for_status()
            data = r.json()
            # If AVM only, treat as "one comp"
            est = float(data.get("price") or data.get("value") or 0) if isinstance(data, dict) else 0
            return [{"sale_price": est}]

    # CUSTOM fallback: no comps available
    return []

async def enrich_deal_with_arv(deal: Deal) -> Dict[str, Any]:
    comps = await fetch_comps(deal)
    out = arv_from_comps(comps)
    # Store on deal if you have these columns; otherwise store in notes/meta/json
    if out["arv"]:
        if hasattr(deal, "arv"):
            deal.arv = out["arv"]
        if hasattr(deal, "arv_confidence"):
            deal.arv_confidence = out["confidence"]
    return out
