  # app/services/scoring.py

from app.models.deal import Deal


def score_deal(deal: Deal) -> Deal:
    """
    Basic scoring engine (Level 2 foundation)
    Calculates:
    - MAO
    - Spread
    - Profit flag (green/orange/red)
    - Confidence score
    """

    # Safety defaults
    arv = deal.arv_estimated or 0
    repairs = deal.repair_estimate or 0
    seller_price = deal.seller_price or 0

    # MAO formula (70% rule)
    mao = (arv * 0.7) - repairs
    deal.mao = round(mao, 2)

    # Spread
    spread = mao - seller_price
    deal.spread = round(spread, 2)

    # Profit flag logic
    if spread > 20000:
        deal.profit_flag = "green"
    elif spread > 5000:
        deal.profit_flag = "orange"
    else:
        deal.profit_flag = "red"

    # Confidence scoring
    confidence = 50

    if deal.profit_flag == "green":
        confidence += 30
    if arv > 0:
        confidence += 10
    if repairs < 50000:
        confidence += 10

    deal.confidence_score = min(confidence, 100)

    return deal
