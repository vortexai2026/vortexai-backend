from app.database import fetch_all

def generate_daily_report():
    actions = fetch_all("""
        SELECT level, action, reason
        FROM ai_activity_log
        WHERE created_at::date = CURRENT_DATE
    """)

    lines = ["🧠 DAILY AI REPORT\n"]

    for a in actions:
        lines.append(
            f"Level {a['level']} → {a['action']} ({a['reason']})"
        )

    return "\n".join(lines)
