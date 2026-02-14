from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True)
    title = Column(String)
    asset_type = Column(String)
    city = Column(String)

    price = Column(Float)
    arv = Column(Float)
    repairs = Column(Float)

    score = Column(Float)

    status = Column(String(30), nullable=False, default="NEW")

    ai_decision = Column(String)
    matched_buyer_id = Column(Integer)

    expected_profit = Column(Float)
    assignment_fee = Column(Float)
    actual_profit = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
