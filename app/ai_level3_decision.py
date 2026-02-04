def decide_action(deal, scores):
    if (
        scores["profit_score"] >= 60
        and scores["urgency_score"] >= 60
        and scores["risk_score"] <= 40
    ):
        return "contact_seller"

    return "ignore"
