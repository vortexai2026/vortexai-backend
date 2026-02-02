from app.database import execute

def record_profit(deal_id: str, profit: float):
    execute("""
        UPDATE deals
        SET profit_realized=%s, status='sold'
        WHERE id=%s
    """, (profit, deal_id))
