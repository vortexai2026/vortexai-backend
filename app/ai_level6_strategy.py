from app.database import fetch_all

def strategy_summary():
    rows = fetch_all("""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE decision='contact_seller') as contacted,
            AVG(ai_score) as avg_score
        FROM deals
    """)
    return rows[0]
