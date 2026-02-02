from app.ai_level2_scoring import score_deal
from app.ai_level3_decision import decide_action
from app.ai_level4_action import take_action
from app.database import fetch_all

def run_cycle():
    deals = fetch_all("SELECT * FROM deals WHERE processed=false")

    for deal in deals:
        scores = score_deal(deal)
        decision = decide_action(scores)

        if decision == "KEEP":
            deal.update(scores)
            take_action(deal)
