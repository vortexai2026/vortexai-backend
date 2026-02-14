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

    # --- AI Fields ---
    score = Column(Float, default=0.0)
    ai_decision = Column(String, default="pending")
    status = Column(String, default="new")  # new, processed, matched, closed
    matched_buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
