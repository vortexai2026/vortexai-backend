from fastapi import FastAPI, Form
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    asset_type = Column(String)
    location = Column(String)
    budget = Column(String)
    tier = Column(String, default="free")

app = FastAPI()

@app.post("/buyers/apply")
def apply_buyer(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    asset_type: str = Form(...),
    location: str = Form(...),
    budget: str = Form("")
):
    db = Session()
    buyer = Buyer(
        name=name,
        email=email,
        phone=phone,
        asset_type=asset_type,
        location=location,
        budget=budget
    )
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return {"ok": True, "buyer_id": buyer.id}

