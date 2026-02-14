# app/models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    full_name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)

    # Preferences
    asset_type = Column(String(50), default="real_estate", nullable=False)  # real_estate, cars, etc
    city = Column(String(120), nullable=True)
    min_budget = Column(Float, default=0.0, nullable=False)
    max_budget = Column(Float, default=999999999.0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
    matched_deals = relationship("Deal", back_populates="matched_buyer")


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True)

    title = Column(String(200), nullable=False)
    asset_type = Column(String(50), default="real_estate", nullable=False)
    city = Column(String(120), nullable=True)

    price = Column(Float, nullable=False)
    arv = Column(Float, nullable=True)          # after repair value (optional)
    repairs = Column(Float, nullable=True)      # repairs estimate (optional)

    source = Column(String(120), nullable=True)
    description = Column(Text, nullable=True)

    # ✅ AI scoring (persisted)
    profit_score = Column(Float, default=0.0, nullable=False)
    urgency_score = Column(Float, default=0.0, nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False)
    ai_score = Column(Float, default=0.0, nullable=False)

    # ✅ AI decision + lifecycle
    ai_decision = Column(String(50), default="unscored", nullable=False)  # ignore/review/contact_seller/notify_buyers
    status = Column(String(50), default="new", nullable=False)            # new/scored/review/contacted/matched/under_contract/sold/dead

    # ✅ money tracking
    profit_realized = Column(Float, nullable=True)

    # ✅ who this deal is matched to
    matched_buyer_id = Column(Integer, ForeignKey("buyers.id", ondelete="SET NULL"), nullable=True)
    matched_buyer = relationship("Buyer", back_populates="matched_deals")

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# helpful indexes
Index("ix_deals_asset_city_price", Deal.asset_type, Deal.city, Deal.price)
Index("ix_deals_status", Deal.status)
Index("ix_deals_ai_score", Deal.ai_score)


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("buyer_id", name="uq_subscription_buyer_id"),)

    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False)

    # Free / Pro / Elite
    tier = Column(String(20), default="free", nullable=False)

    # Optional Stripe fields (you can wire later)
    stripe_customer_id = Column(String(120), nullable=True)
    stripe_subscription_id = Column(String(120), nullable=True)

    active = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    buyer = relationship("Buyer")
