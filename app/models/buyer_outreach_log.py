from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class BuyerOutreachLog(Base):
    __tablename__ = "buyer_outreach_log"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False)

    channel = Column(String(20), nullable=False, default="email")
    subject = Column(Text)
    body = Column(Text)

    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), nullable=False, default="SENT")  # SENT / FAILED
    error = Column(Text)
