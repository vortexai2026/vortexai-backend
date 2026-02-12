from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    city = Column(String, nullable=False)
    state = Column(String, nullable=True)
    asset_type = Column(String, nullable=False)  # house, condo, land, multi-family
    min_budget = Column(Float, nullable=False)
    max_budget = Column(Float, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=True)

    asset_type = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
