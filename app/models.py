from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


# =============================
# USERS
# =============================
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =============================
# BUYERS
# =============================
class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    full_name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)

    # Preferences
    asset_type = Column(String(50), default="real_estate", nullable=False)
    city = Column(String(120), nullable=True)
    min_budget = Column(Float, default=0.0, nullable=False)
    max_budget = Column(Float, default=999999999.0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")


# =============================
# DEALS (AI UPGRADED)
# =============================
class Deal(Base):
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(200), nullable=False)
    asset_type = Column(String(50), default="real_estate", nullable=False)
    city = Column(String(120), nullable=True)

    price = Column(Float, nullable=False)
    arv = Column(Float, nullable=True)
    repairs = Column(Float, nullable=True)

    source = Column(String(120), nullable=True)
    description = Column(Text, nullable=True)

    # -------------------------
    # AI SCORING FIELDS
    # -------------------------
    profit_score = Column(Float, default=0)
    urgency_score = Column(Float, default=0)
    risk_score = Column(Float, default=0)
    ai_score = Column(Float, default=0)

    ai_decision = Column(String(50), nullable=True)

    # -------------------------
    # LIFECYCLE
    # -------------------------
    status = Column(String(50), default="new")  
    # new / contacted / matched / under_contract / sold / dead

    profit_realized = Column(Float, nullable=True)

    matched_buyer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("buyers.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    matched_buyer = relationship("Buyer")


# =============================
# SUBSCRIPTIONS
# =============================
class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("buyer_id", name="uq_subscription_buyer_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False)

    tier = Column(String(20), default="free", nullable=False)

    stripe_customer_id = Column(String(120), nullable=True)
    stripe_subscription_id = Column(String(120), nullable=True)

    active = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    buyer = relationship("Buyer")
