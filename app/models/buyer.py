# app/models/buyer.py
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)

    # core identity
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)

    # segmentation
    asset_type = Column(String, nullable=True)   # e.g. "sfh", "multi"
    city = Column(String, nullable=True)         # optional
    market_tag = Column(String, nullable=True, index=True)

    # budgets
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    max_budget = Column(Float, nullable=True)    # legacy column in your DB

    # buy box
    buy_box_beds = Column(Integer, nullable=True)
    buy_box_baths = Column(Float, nullable=True)

    # verification
    proof_of_funds = Column(String, nullable=True)

    # ops + analytics
    tier = Column(String, nullable=True, default="free")  # free/pro/vip
    is_active = Column(Boolean, nullable=True, default=True)
    status = Column(String, nullable=True, default="active")
    notes = Column(Text, nullable=True)

    total_matches = Column(Integer, nullable=True, default=0)
    total_deals_closed = Column(Integer, nullable=True, default=0)
    monthly_match_count = Column(Integer, nullable=True, default=0)
    monthly_match_reset_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
