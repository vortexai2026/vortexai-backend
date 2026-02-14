from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    asset_type = Column(String, nullable=False)
    city = Column(String, nullable=False)
    max_budget = Column(Float, nullable=False)

    tier = Column(String, default="free")  # free, pro, elite
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
