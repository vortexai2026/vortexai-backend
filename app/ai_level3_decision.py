def decide_action(deal, scores):
    ai = scores.get("ai_score", 0)
    profit = scores.get("profit_score", 0)
    urgency = scores.get("urgency_score", 0)
    risk = scores.get("risk_score", 0)

    # HARD FILTER
    if risk >= 80:
        return "ignore"

    # HOT DEAL
    if ai >= 70 and profit >= 65:
        return "notify_buyers"

    # REVIEW DEAL
    if ai >= 45 or (profit >= 60 and urgency >= 40):
        return "review"

    return "ignore"
