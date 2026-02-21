from typing import Tuple


def estimate_repairs(property_data: dict) -> float:
    """
    Very simple repair estimator.
    You can upgrade this later with ML or comps logic.
    """

    year_built = property_data.get("year_built")
    square_feet = property_data.get("square_feet", 0)

    if not year_built:
        return 25000

    age = 2026 - year_built

    # Basic logic
    if age < 20:
        return square_feet * 5
    elif age < 50:
        return square_feet * 12
    else:
        return square_feet * 20


def compute_score(
    seller_price: float,
    arv: float,
    repairs: float
) -> Tuple[str, float, float]:
    """
    Returns:
    - profit_flag (green/orange/red)
    - spread
    - mao (max allowable offer)
    """

    if not seller_price or not arv:
        return "red", 0, 0

    mao = (arv * 0.7) - repairs
    spread = mao - seller_price

    if spread >= 20000:
        return "green", spread, mao
    elif spread >= 5000:
        return "orange", spread, mao
    else:
        return "red", spread, mao
