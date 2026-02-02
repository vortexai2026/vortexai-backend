from app.database import execute

def log_feedback(deal_id: int, outcome: str):
    execute(
        "INSERT INTO deal_feedback (deal_id, outcome) VALUES (%s, %s)",
        (deal_id, outcome)
    )
