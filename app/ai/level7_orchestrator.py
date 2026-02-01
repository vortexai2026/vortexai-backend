import time
from app.database import fetch_all, execute
from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import next_action
from app.ai_level6_strategy import strategy_boost
from app.ai_level5_learning import learn_adjustment

POLL_INTERVAL_SECONDS = 60  # run every minute


def process_deal(deal: dict):
    # STEP 1 — SCORE
    scores = score_deal(deal)

    # STEP 2 — STRATEGY BOOST
    boost = strategy_boost(deal.get("location"), deal.get("asset_type"))
    scores["ai_score"] = round(min(100, scores["ai_score"] * (1 + boost)), 2)

    # STEP 3 — DECISION
    decision = decide_action(scores)

    # STEP 4 — ACTION
    action = next_action(decision)

    # STEP 5 — SAVE RESULTS
    execute(
        """
        UPDATE deals
        SET ai_score=%s,
            decision=%s,
            action=%s,
            status='processed'
        WHERE id=%s
        """,
        (
            scores["ai_score"],
            decision,
            action,
            deal["id"]
        )
    )

    return decision, action


def learning_loop():
    """
    Learns from completed deals
    """
    completed = fetch_all(
        """
        SELECT id, outcome
        FROM deals
        WHERE outcome IS NOT NULL
          AND learned IS NOT TRUE
        """
    )

    for deal in completed:
        adjustment = learn_adjustment(deal["outcome"])

        execute(
            """
            UPDATE deals
            SET learning_adjustment=%s,
                learned=TRUE
            WHERE id=%s
            """,
            (adjustment, deal["id"])
        )


def run():
    print("🤖 VortexAI Level 7 Orchestrator running...")

    while True:
        try:
            # STEP A — FETCH NEW DEALS
            deals = fetch_all(
                """
                SELECT *
                FROM deals
                WHERE status='new'
                ORDER BY created_at ASC
                LIMIT 25
                """
            )

            for deal in deals:
                decision, action = process_deal(deal)
                print(f"Deal {deal['id']} → {decision} → {action}")

            # STEP B — LEARN
            learning_loop()

        except Exception as e:
            print("ERROR:", e)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
