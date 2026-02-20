from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    market_tag = Column(String, nullable=True)   # e.g. TX_DFW
    max_price = Column(Float, nullable=True)
    buy_type = Column(String, nullable=True)     # flip/rental/both
    preferred_zip = Column(String, nullable=True)

    proof_of_funds = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
