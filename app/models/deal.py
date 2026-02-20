from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base   # ✅ FIXED IMPORT

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    # ---- Existing core fields ----
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)

    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)
    sqft = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)

    seller_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    status = Column(String, nullable=True, default="Lead")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # ---- Valuation fields ----
    market_tag = Column(String, nullable=True)
    arv_estimated = Column(Float, nullable=True)
    repair_estimate = Column(Float, nullable=True)
    mao = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    profit_flag = Column(String, nullable=True)

    comps_raw = Column(Text, nullable=True)
