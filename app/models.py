from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, Float,
    CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    buyers = relationship("Buyer", back_populates="owner", cascade="all, delete-orphan")


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    city = Column(String(120), nullable=False)
    budget_min = Column(Float, nullable=False)
    budget_max = Column(Float, nullable=False)
    asset_type = Column(String(80), nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    owner = relationship("User", back_populates="buyers")

    __table_args__ = (
        CheckConstraint("budget_min >= 0", name="ck_buyers_budget_min_nonneg"),
        CheckConstraint("budget_max >= 0", name="ck_buyers_budget_max_nonneg"),
        CheckConstraint("budget_max >= budget_min", name="ck_buyers_budget_range"),
        Index("ix_buyers_city_asset", "city", "asset_type"),
    )


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    city = Column(String(120), nullable=False)
    asset_type = Column(String(80), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=False)

    matched_buyer_id = Column(Integer, ForeignKey("buyers.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("price > 0", name="ck_deals_price_gt_zero"),
        Index("ix_deals_city_asset_price", "city", "asset_type", "price"),
    )
