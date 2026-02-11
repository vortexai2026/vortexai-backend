import os
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------------------
# DB
# ----------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ----------------------------
# MODELS
# ----------------------------
class SellerLead(Base):
    __tablename__ = "seller_leads"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    name = Column(String(120), nullable=False)
    phone = Column(String(50), nullable=False)
    asset_type = Column(String(50), nullable=False)  # real_estate, car, watch, business, etc
    location = Column(String(120), nullable=False)
    asking_price = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)


class BuyerLead(Base):
    __tablename__ = "buyer_leads"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    name = Column(String(120), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)

    asset_types = Column(String(300), nullable=False)  # comma list
    budget_min = Column(String(50), nullable=True)
    budget_max = Column(String(50), nullable=True)
    location = Column(String(120), nullable=True)

    tier = Column(String(30), default="free")  # free / paid / enterprise


Base.metadata.create_all(bind=engine)

# ----------------------------
# SCHEMAS
# ----------------------------
class SellerCreate(BaseModel):
    name: str
    phone: str
    asset_type: str
    location: str
    asking_price: Optional[str] = None
    description: Optional[str] = None


class BuyerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    asset_types: List[str]
    budget_min: Optional[str] = None
    budget_max: Optional[str] = None
    location: Optional[str] = None
    tier: str = "free"


# ----------------------------
# ROUTER
# ----------------------------
router = APIRouter(tags=["phase2_intake"])

SELL_FORM_HTML = """
<html>
<head><title>Sell</title></head>
<body style="font-family: Arial; max-width: 700px; margin: 40px auto;">
<h2>Seller Intake Form</h2>
<form method="post" action="/sell">
  <label>Name</label><br><input name="name" required style="width:100%;padding:8px;"><br><br>
  <label>Phone</label><br><input name="phone" required style="width:100%;padding:8px;"><br><br>
  <label>Asset Type (real_estate, car, watch, business)</label><br>
  <input name="asset_type" required style="width:100%;padding:8px;"><br><br>
  <label>Location</label><br><input name="location" required style="width:100%;padding:8px;"><br><br>
  <label>Asking Price</label><br><input name="asking_price" style="width:100%;padding:8px;"><br><br>
  <label>Description</label><br><textarea name="description" style="width:100%;padding:8px;" rows="5"></textarea><br><br>
  <button type="submit" style="padding:10px 16px;">Submit</button>
</form>
</body>
</html>
"""

BUY_FORM_HTML = """
<html>
<head><title>Buyers Apply</title></head>
<body style="font-family: Arial; max-width: 700px; margin: 40px auto;">
<h2>Buyer Application</h2>
<form method="post" action="/buyers/apply">
  <label>Name</label><br><input name="name" required style="width:100%;padding:8px;"><br><br>
  <label>Email</label><br><input name="email" required style="width:100%;padding:8px;"><br><br>
  <label>Phone</label><br><input name="phone" style="width:100%;padding:8px;"><br><br>
  <label>Asset Types (comma separated, e.g. real_estate,cars,watches)</label><br>
  <input name="asset_types" required style="width:100%;padding:8px;"><br><br>
  <label>Budget Min</label><br><input name="budget_min" style="width:100%;padding:8px;"><br><br>
  <label>Budget Max</label><br><input name="budget_max" style="width:100%;padding:8px;"><br><br>
  <label>Location</label><br><input name="location" style="width:100%;padding:8px;"><br><br>
  <label>Tier (free/paid/enterprise)</label><br><input name="tier" value="free" style="width:100%;padding:8px;"><br><br>
  <button type="submit" style="padding:10px 16px;">Submit</button>
</form>
</body>
</html>
"""

@router.get("/sell", response_class=HTMLResponse)
def sell_form():
    return SELL_FORM_HTML

@router.post("/sell")
def sell_submit(
    name: str = Form(...),
    phone: str = Form(...),
    asset_type: str = Form(...),
    location: str = Form(...),
    asking_price: str = Form(""),
    description: str = Form(""),
):
    db = SessionLocal()
    try:
        lead = SellerLead(
            name=name.strip(),
            phone=phone.strip(),
            asset_type=asset_type.strip().lower(),
            location=location.strip(),
            asking_price=asking_price.strip() or None,
            description=description.strip() or None,
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return {"ok": True, "seller_lead_id": lead.id}
    finally:
        db.close()

@router.get("/buyers/apply", response_class=HTMLResponse)
def buyers_form():
    return BUY_FORM_HTML

@router.post("/buyers/apply")
def buyers_submit(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    asset_types: str = Form(...),
    budget_min: str = Form(""),
    budget_max: str = Form(""),
    location: str = Form(""),
    tier: str = Form("free"),
):
    db = SessionLocal()
    try:
        types_clean = ",".join([t.strip().lower() for t in asset_types.split(",") if t.strip()])
        lead = BuyerLead(
            name=name.strip(),
            email=email.strip().lower(),
            phone=phone.strip() or None,
            asset_types=types_clean,
            budget_min=budget_min.strip() or None,
            budget_max=budget_max.strip() or None,
            location=location.strip() or None,
            tier=tier.strip().lower() or "free",
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return {"ok": True, "buyer_lead_id": lead.id, "tier": lead.tier}
    finally:
        db.close()

@router.get("/admin/sellers")
def list_sellers(limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.query(SellerLead).order_by(SellerLead.created_at.desc()).limit(limit).all()
        return {"count": len(rows), "items": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat(),
                "name": r.name,
                "phone": r.phone,
                "asset_type": r.asset_type,
                "location": r.location,
                "asking_price": r.asking_price,
                "description": r.description,
            } for r in rows
        ]}
    finally:
        db.close()

@router.get("/admin/buyers")
def list_buyers(limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.query(BuyerLead).order_by(BuyerLead.created_at.desc()).limit(limit).all()
        return {"count": len(rows), "items": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat(),
                "name": r.name,
                "email": r.email,
                "phone": r.phone,
                "asset_types": r.asset_types,
                "budget_min": r.budget_min,
                "budget_max": r.budget_max,
                "location": r.location,
                "tier": r.tier,
            } for r in rows
        ]}
    finally:
        db.close()

# Optional: If you want to run this file alone for testing
def create_app() -> FastAPI:
    app = FastAPI(title="Phase 2 - Intake")
    app.include_router(router)
    return app

app = create_app()
