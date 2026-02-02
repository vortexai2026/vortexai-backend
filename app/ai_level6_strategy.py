from app.database import fetch_all

def weekly_strategy():
    results = fetch_all("""
        SELECT asset_type, COUNT(*) 
        FROM deal_feedback 
        WHERE outcome='closed'
        GROUP BY asset_type
    """)

    return {
        "focus_more_on": max(results, key=lambda x: x[1])[0] if results else None
    }
