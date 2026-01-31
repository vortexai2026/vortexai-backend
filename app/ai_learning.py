"""
VortexAI – Learning & Adjustment Engine (Level 3)

This module adjusts AI scoring weights based on real outcomes.
"""

from typing import Dict

# Default learning memory (can later be stored in DB)
LEARNING_STATE = {
    "profit_weight": 1.0,
    "urgency_weight": 1.0,
    "risk_weight": 1.0
}

def learn_adjustment(outcome: str) -> float:
    """
    Returns a learning multiplier based on outcome
    """
    outcome = (outcome or "").lower()

    if outcome in ("sold", "closed", "profit", "success"):
        return 0.10

    if outcome in ("failed", "scam", "loss", "dead"):
        return -0.10

    return 0.0


def apply_learning(outcome: str) -> Dict[str, float]:
    """
    Adjust internal AI weights based on outcome
    """
    delta = learn_adjustment(outcome)

    LEARNING_STATE["profit_weight"] = max(0.5, LEARNING_STATE["profit_weight"] + delta)
    LEARNING_STATE["urgency_weight"] = max(0.5, LEARNING_STATE["urgency_weight"] + delta / 2)
    LEARNING_STATE["risk_weight"] = max(0.5, LEARNING_STATE["risk_weight"] - delta)

    return LEARNING_STATE


def score_deal(base_scores: Dict[str, float]) -> float:
    """
    Applies learning weights to base AI scores
    """
    profit = base_scores.get("profit", 0)
    urgency = base_scores.get("urgency", 0)
    risk = base_scores.get("risk", 0)

    final_score = (
        profit * LEARNING_STATE["profit_weight"] +
        urgency * LEARNING_STATE["urgency_weight"] -
        risk * LEARNING_STATE["risk_weight"]
    )

    return round(max(0, min(final_score, 100)), 2)
