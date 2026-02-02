# app/ai_level5_learning.py

from typing import Dict

"""
LEVEL 5 — LEARNING AI

This layer adjusts AI behavior based on REAL outcomes.
It MUST expose: learn_adjustment()
"""


def learn_adjustment(outcome: str) -> float:
    """
    Returns a numeric adjustment based on deal outcome.
    Positive = reward
    Negative = penalty
    """

    if not outcome:
        return 0.0

    outcome = outcome.lower().strip()

    # ✅ SUCCESS OUTCOMES
    if outcome in ("sold", "closed", "profit", "won", "deal_closed"):
        return 0.10

    # ❌ FAILURE OUTCOMES
    if outcome in ("failed", "loss", "scam", "bad", "no_response"):
        return -0.10

    # 😐 NEUTRAL / UNKNOWN
    return 0.0


def apply_learning(scores: Dict[str, float], adjustment: float) -> Dict[str, float]:
    """
    Apply learning adjustment to AI score.
    """

    scores = scores.copy()

    ai_score = scores.get("ai_score", 0)
    ai_score += ai_score * adjustment

    # Clamp
    scores["ai_score"] = max(0, min(100, round(ai_score, 2)))

    return scores
