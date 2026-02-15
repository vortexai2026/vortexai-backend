# app/models/offer_log.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from app.database import Base

class OfferLog(Base):
    __tablename__ = "offer_logs"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)

    offer_price = Column(Numeric, nullable=False)
    offered_at = Column(DateTime(timezone=True), server_default=func.now())

    channel = Column(String(20), default="email")
    recipient = Column(Text)
    subject = Column(Text)
    body = Column(Text)

    status = Column(String(20), default="SENT")  # SENT / FAILED
    error = Column(Text)
