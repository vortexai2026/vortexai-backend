from app.ai_failsafe import failsafe_check
from app.ai_source_health import evaluate_sources
from app.ai_level6_strategy import run_strategy
from app.ai_activity_log import log_ai_action

def run_orchestrator():
    failsafe_check()

    evaluate_sources()
    log_ai_action(7, "SOURCE_EVAL", "Checked source health")

    run_strategy()
    log_ai_action(7, "STRATEGY_RUN", "Updated priorities")
