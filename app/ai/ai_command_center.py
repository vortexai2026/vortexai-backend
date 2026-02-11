from app.database import fetch_all

def status_snapshot():
    return {
        "top_assets": fetch_all("""
            SELECT asset_type, COUNT(*) 
            FROM deals 
            GROUP BY asset_type
            ORDER BY COUNT DESC
        """),
        "recent_actions": fetch_all("""
            SELECT action, reason
            FROM ai_activity_log
            ORDER BY created_at DESC
            LIMIT 20
        """)
    }
