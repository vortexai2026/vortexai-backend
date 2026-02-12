from app.database import fetch_all, execute


def ingest_source(source_name: str) -> int:
    """
    Generic ingestion handler.
    You can expand this later to scrape, fetch APIs, or process files.
    For now, it simply marks deals from a source as 'ingested'.
    """

    # Count deals from this source
    rows = fetch_all("SELECT id FROM deals WHERE source=%s", (source_name,))
    count = len(rows)

    # Mark them as ingested
    execute("""
        UPDATE deals
        SET ingested = TRUE
        WHERE source = %s
    """, (source_name,))

    return count
