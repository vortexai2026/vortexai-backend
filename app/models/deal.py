from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.db import Base  # adjust import to your Base

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    # ---- Existing core fields (keep yours; add if missing) ----
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)

    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)
    sqft = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)

    seller_price = Column(Float, nullable=True)   # asking price
    notes = Column(Text, nullable=True)           # distress keywords, etc.

    status = Column(String, nullable=True, default="Lead")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # ---- NEW valuation fields ----
    market_tag = Column(String, nullable=True)          # TX_DFW / GA_ATL
    arv_estimated = Column(Float, nullable=True)
    repair_estimate = Column(Float, nullable=True)
    mao = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    profit_flag = Column(String, nullable=True)         # green/orange/red

    comps_raw = Column(Text, nullable=True)             # optional: store raw JSON as string
