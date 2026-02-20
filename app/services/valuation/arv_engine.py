from __future__ import annotations

def calculate_arv(comps: dict) -> float | None:
    """
    Prefer median price when available.
    """
    median_price = comps.get("median_price")
    if isinstance(median_price, (int, float)):
        return float(median_price)

    avg_price = comps.get("avg_price")
    if isinstance(avg_price, (int, float)):
        return float(avg_price)

    return None

def calculate_mao(arv: float, repairs: float) -> float:
    return (arv * 0.70) - repairs

def calculate_spread(arv: float, repairs: float, seller_price: float) -> float:
    return arv - repairs - seller_price
