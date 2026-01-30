from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    asset_type = Column(String)
    location = Column(String)
    tier = Column(String)

class Deal(Base):
    __tablename__ = "deals"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String)
    asset_type = Column(String)
    location = Column(String)
    price = Column(String)
    status = Column(String, default="new")
    matched_buyer_id = Column(Integer)
    notes = Column(Text)

