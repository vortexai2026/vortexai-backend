from typing import Dict

def region_strategy(location: str, asset_type: str) -> Dict[str, str]:
    loc = (location or "").lower()
    at = (asset_type or "").lower()

    if "winnipeg" in loc and at == "real_estate":
        return {"strategy": "wholesale", "note": "focus on motivated sellers, under 250k"}
    if "toronto" in loc and at == "real_estate":
        return {"strategy": "off-market", "note": "Toronto is competitive; require stronger margins"}
    if at in ("cars", "car"):
        return {"strategy": "flip", "note": "focus on clean title and under 12k buys"}
    return {"strategy": "general", "note": "default strategy rules"}
