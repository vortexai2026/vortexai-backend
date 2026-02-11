from app.database import fetch_all

def strategy_summary():
    rows = fetch_all("""
        SELECT decision, COUNT(*) as count
        FROM deals
        GROUP BY decision
        ORDER BY count DESC
    """)
    return {"decisions": rows}
