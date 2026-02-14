from .ingest import IngestPayload, IngestDealIn

# If you already have other schema files like:
# buyer.py, deal.py, etc.
# Add them here as well (safe to include even if not used everywhere)

try:
    from .buyer import BuyerCreate, BuyerOut
except Exception:
    pass

try:
    from .deal import DealCreate, DealOut
except Exception:
    pass

__all__ = [
    "IngestPayload",
    "IngestDealIn",
]

