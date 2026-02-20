from __future__ import annotations

def estimate_repairs(
    *,
    year_built: int | None,
    sqft: int | None,
    distress_keywords: str | None,
) -> float:
    """
    V1 heuristic repair estimator:
    - Baseline $15k
    - Older homes + more repairs
    - Distress keywords increase repairs
    - Sqft adds scaling
    """
    repairs = 15000.0

    if year_built is not None:
        if year_built < 1970:
            repairs += 20000
        elif year_built < 1990:
            repairs += 12000
        elif year_built < 2005:
            repairs += 6000

    if sqft is not None:
        # mild scaling
        if sqft > 2200:
            repairs += 6000
        elif sqft > 1600:
            repairs += 3000

    text = (distress_keywords or "").lower()
    bumps = [
        ("fire", 35000),
        ("water damage", 20000),
        ("mold", 15000),
        ("foundation", 25000),
        ("roof", 12000),
        ("as-is", 8000),
        ("needs work", 12000),
        ("handyman", 10000),
        ("vacant", 5000),
        ("foreclosure", 10000),
        ("probate", 7000),
        ("tenant", 6000),
    ]
    for k, add in bumps:
        if k in text:
            repairs += add

    # guardrails
    if repairs < 10000:
        repairs = 10000
    if repairs > 120000:
        repairs = 120000

    return float(repairs)
