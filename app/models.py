from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


# ---------------- USERS ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

    buyers = relationship("Buyer", back_populates="owner")


# ---------------- BUYERS ----------------
class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    phone = Column(String)
    city = Column(String)
    budget_min = Column(Float)
    budget_max = Column(Float)
    asset_type = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="buyers")

    deals = relationship("Deal", back_populates="matched_buyer")


# ---------------- DEALS ----------------
class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    city = Column(String)
    asset_type = Column(String)
    price = Column(Float)
    description = Column(String)

    matched_buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True)
    matched_buyer = relationship("Buyer", back_populates="deals")
