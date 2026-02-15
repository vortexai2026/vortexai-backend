from sqlalchemy import Column, Integer, Text, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"))
    note = Column(Text)
    due_date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
