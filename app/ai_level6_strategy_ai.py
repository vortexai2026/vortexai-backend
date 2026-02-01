def strategy_boost(location: str, asset_type: str) -> float:
    """
    Level 6 Strategy AI
    """

    location = (location or "").lower()
    asset_type = (asset_type or "").lower()

    boost = 0.0

    # Strong regions
    strong_cities = [
        "toronto", "vancouver", "calgary",
        "winnipeg", "edmonton", "miami",
        "phoenix", "dallas", "atlanta"
    ]

    if any(city in location for city in strong_cities):
        boost += 0.05

    # Strong categories
    if asset_type in ("real_estate", "cars", "business"):
        boost += 0.05

    return boost

