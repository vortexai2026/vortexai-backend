from app.database import fetch_all, execute

def evaluate_sources():
    sources = fetch_all("""
        SELECT source,
               COUNT(*) as total,
               SUM(CASE WHEN status='sold' THEN 1 ELSE 0 END) as sold
        FROM deals
        GROUP BY source
    """)

    for s in sources:
        total = s["total"]
        sold = s["sold"] or 0
        ratio = sold / total if total else 0

        status = "active"
        if total > 20 and ratio < 0.02:
            status = "disabled"

        execute("""
            UPDATE sources
            SET status=%s, success_ratio=%s
            WHERE name=%s
        """, (status, ratio, s["source"]))
