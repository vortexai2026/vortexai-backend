from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class BuyerInterest(Base):
    __tablename__ = "buyer_interests"

    id = Column(Integer, primary_key=True, index=True)

    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)

    status = Column(String, default="interested")  # interested, not_interested, contacted, under_contract, closed

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("buyer_id", "deal_id", name="uq_buyer_deal_interest"),
    )
