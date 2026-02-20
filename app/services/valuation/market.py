from __future__ import annotations

def market_tag(city: str | None, state: str | None) -> str | None:
    """
    Minimal mapping for 2-city strategy:
    - Dallas–Fort Worth, TX => TX_DFW
    - Atlanta, GA => GA_ATL
    """
    if not city or not state:
        return None

    c = city.strip().lower()
    s = state.strip().upper()

    if s == "TX" and ("dallas" in c or "fort worth" in c or "arlington" in c or "plano" in c or "irving" in c):
        return "TX_DFW"

    if s == "GA" and ("atlanta" in c or "marietta" in c or "decatur" in c or "sandy springs" in c):
        return "GA_ATL"

    # Optional: if you ingest exact city names only, this still works:
    if s == "TX" and c == "dallas":
        return "TX_DFW"
    if s == "GA" and c == "atlanta":
        return "GA_ATL"

    return None
