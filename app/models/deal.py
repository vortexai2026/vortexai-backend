from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    city = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    # Existing scoring field
    score = Column(Float, default=0.0)

    # Lifecycle engine
    status = Column(String, default="new")  # new, ai_processed, matched, contacted, under_contract, closed, dead

    # AI decision + matching
    ai_decision = Column(String, default="pending")  # pending, ignore, review, match_buyer, contact_seller
    matched_buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True)
    ai_processed_at = Column(DateTime(timezone=True), nullable=True)

    # Profit visibility
    arv = Column(Float, nullable=True)
    repairs = Column(Float, nullable=True)
    expected_profit = Column(Float, nullable=True)
    assignment_fee = Column(Float, nullable=True)
    actual_profit = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
