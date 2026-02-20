from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    market_tag = Column(String, nullable=False)  # TX_DFW or GA_ATL

    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)

    buy_box_beds = Column(Integer, nullable=True)
    buy_box_baths = Column(Float, nullable=True)

    proof_of_funds = Column(String, nullable=True)  # file link or yes/no
    notes = Column(String, nullable=True)

    status = Column(String, default="active")  # active / paused

    created_at = Column(DateTime(timezone=True), server_default=func.now())
