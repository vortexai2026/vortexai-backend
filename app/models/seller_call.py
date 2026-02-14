# app/models/seller_call.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from app.database import Base

class SellerCall(Base):
    __tablename__ = "seller_calls"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"))

    call_date = Column(DateTime(timezone=True), server_default=func.now())
    motivation_level = Column(Integer)
    asking_price = Column(Numeric)
    timeline = Column(String(100))
    notes = Column(Text)
    next_followup_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
