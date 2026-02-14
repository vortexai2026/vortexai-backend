from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, UniqueConstraint
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

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


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
