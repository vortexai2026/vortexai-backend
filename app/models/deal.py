# app/models/deal.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # address/location
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)

    market_tag = Column(String, nullable=True)

    # property details
    square_feet = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)
    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)

    # pricing
    seller_price = Column(Float, nullable=True)
    arv_estimated = Column(Float, nullable=True)
    repair_estimate = Column(Float, nullable=True)
    mao = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)

    # status flag
    profit_flag = Column(String, nullable=False, default="red")  # green/orange/red
