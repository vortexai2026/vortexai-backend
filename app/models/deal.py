from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    city = Column(String, nullable=False)

    price = Column(Float, nullable=False)
    score = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
