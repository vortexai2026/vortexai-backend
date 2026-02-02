from app.database import fetch_one, execute

def update_confidence(success: bool):
    delta = 0.05 if success else -0.05
    execute("""
        UPDATE ai_state
        SET confidence = GREATEST(0, LEAST(1, confidence + %s))
    """, (delta,))
