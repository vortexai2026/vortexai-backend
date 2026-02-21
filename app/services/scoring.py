from app.models.deal import Deal


def score_deal(deal: Deal) -> Deal:
    """
    Simple 70% rule scoring engine
    """

    if not deal.arv_estimated or not deal.repair_estimate:
        deal.profit_flag = "red"
        deal.confidence_score = 0
        return deal

    # 70% Rule
    mao = (deal.arv_estimated * 0.70) - deal.repair_estimate
    deal.mao = mao

    if deal.seller_price and deal.seller_price <= mao:
        deal.profit_flag = "green"
        deal.confidence_score = 85
    elif deal.seller_price and deal.seller_price <= mao * 1.1:
        deal.profit_flag = "orange"
        deal.confidence_score = 60
    else:
        deal.profit_flag = "red"
        deal.confidence_score = 30

    deal.spread = (
        deal.arv_estimated - deal.seller_price - deal.repair_estimate
        if deal.seller_price else 0
    )

    return deal
