import uuid
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class CarInventory(Base):
    __tablename__ = "car_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_number = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    km = Column(Integer, nullable=True)
    engine = Column(String, nullable=True)
    transmission = Column(String, nullable=True)
    features = Column(Text, nullable=True)
    cost = Column(Numeric, nullable=True)
    asking_price = Column(Numeric, nullable=True)
    status = Column(String, nullable=False, default="available")  # available/reserved/sold
    posted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CarLead(Base):
    __tablename__ = "car_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey("car_inventory.id", ondelete="CASCADE"), nullable=True)
    lead_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    source = Column(String, nullable=True)  # facebook/kijiji/referral
    message = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="new")  # new/contacted/appointment/closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CarMessage(Base):
    __tablename__ = "car_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("car_leads.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String, nullable=False)  # inbound/outbound
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CarSale(Base):
    __tablename__ = "car_sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey("car_inventory.id", ondelete="CASCADE"), nullable=False)
    sold_price = Column(Numeric, nullable=True)
    profit = Column(Numeric, nullable=True)
    commission = Column(Numeric, nullable=True)
    sold_at = Column(DateTime(timezone=True), server_default=func.now())
