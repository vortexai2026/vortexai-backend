from sqlalchemy import Column, BigInteger, Integer, Text, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class AIDecisionLog(Base):
    __tablename__ = "ai_decision_log"

    id = Column(BigInteger, primary_key=True, index=True)

    deal_id = Column(Integer, nullable=True, index=True)
    buyer_id = Column(Integer, nullable=True, index=True)

    decision = Column(Text, nullable=True)
    status = Column(Text, nullable=True)

    score = Column(Float, nullable=True)
    expected_profit = Column(Float, nullable=True)

    error = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
