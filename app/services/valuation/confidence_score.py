from __future__ import annotations

def calculate_confidence(
    *,
    comps_count: int,
    has_address: bool,
    has_sqft: bool,
    has_beds_baths: bool,
) -> int:
    """
    V1 confidence:
    - Starts at 40
    - More comps => higher
    - More property details => higher
    """
    score = 40

    if comps_count >= 8:
        score += 25
    elif comps_count >= 5:
        score += 18
    elif comps_count >= 3:
        score += 10
    else:
        score -= 10

    if has_address:
        score += 10
    if has_sqft:
        score += 10
    if has_beds_baths:
        score += 10

    if score < 0:
        score = 0
    if score > 100:
        score = 100
    return int(score)
