from app.config.money_rules import SCORING_THRESHOLDS

def decide_action(scores: dict) -> str:
    if (
        scores["profit"] >= SCORING_THRESHOLDS["min_profit"]
        and scores["urgency"] >= SCORING_THRESHOLDS["min_urgency"]
        and scores["risk"] <= SCORING_THRESHOLDS["max_risk"]
    ):
        return "KEEP"
    return "SKIP"
