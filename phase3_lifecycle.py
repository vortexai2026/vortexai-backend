import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ----------------------------
# DEAL MODEL
# ----------------------------
class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, index=True)

    title = Column(String(200), nullable=False)
    asset_type = Column(String(50), nullable=False)     # real_estate / car / watch / business
    location = Column(String(120), nullable=True)
    price = Column(String(50), nullable=True)
    source = Column(String(120), nullable=True)

    status = Column(String(30), default="new", index=True)
    notes = Column(Text, nullable=True)

    matched_buyer_id = Column(Integer, nullable=True)  # (optional) link to buyer_leads.id

Base.metadata.create_all(bind=engine)

ALLOWED_STATUSES = {
    "new",
    "matched",
    "contacted",
    "negotiating",
    "under_contract",
    "sold",
    "failed",
}

# ----------------------------
# SCHEMAS
# ----------------------------
class DealCreate(BaseModel):
    title: str
    asset_type: str
    location: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class DealUpdateStatus(BaseModel):
    status: str
    notes: Optional[str] = None
    matched_buyer_id: Optional[int] = None

# ----------------------------
# ROUTER
# ----------------------------
router = APIRouter(tags=["phase3_lifecycle"])

@router.post("/deals")
def create_deal(payload: DealCreate):
    db = SessionLocal()
    try:
        d = Deal(
            title=payload.title.strip(),
            asset_type=payload.asset_type.strip().lower(),
            location=(payload.location or "").strip() or None,
            price=(payload.price or "").strip() or None,
            source=(payload.source or "").strip() or None,
            notes=(payload.notes or "").strip() or None,
            status="new",
            updated_at=datetime.utcnow(),
        )
        db.add(d)
        db.commit()
        db.refresh(d)
        return {"ok": True, "deal_id": d.id, "status": d.status}
    finally:
        db.close()

@router.get("/deals")
def list_deals(status: Optional[str] = None, limit: int = 50):
    db = SessionLocal()
    try:
        q = db.query(Deal)
        if status:
            q = q.filter(Deal.status == status.strip().lower())
        rows = q.order_by(Deal.created_at.desc()).limit(limit).all()
        return {"count": len(rows), "deals": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                "title": r.title,
                "asset_type": r.asset_type,
                "location": r.location,
                "price": r.price,
                "source": r.source,
                "status": r.status,
                "matched_buyer_id": r.matched_buyer_id,
                "notes": r.notes,
            } for r in rows
        ]}
    finally:
        db.close()

@router.patch("/deals/{deal_id}/status")
def update_status(deal_id: int, payload: DealUpdateStatus):
    new_status = payload.status.strip().lower()
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use: {sorted(ALLOWED_STATUSES)}")

    db = SessionLocal()
    try:
        d = db.query(Deal).filter(Deal.id == deal_id).first()
        if not d:
            raise HTTPException(status_code=404, detail="Deal not found")

        d.status = new_status
        d.updated_at = datetime.utcnow()

        if payload.notes is not None:
            d.notes = payload.notes.strip() or None
        if payload.matched_buyer_id is not None:
            d.matched_buyer_id = payload.matched_buyer_id

        db.commit()
        db.refresh(d)
        return {"ok": True, "deal_id": d.id, "status": d.status, "updated_at": d.updated_at.isoformat()}
    finally:
        db.close()

@router.get("/admin/pipeline")
def pipeline_counts():
    db = SessionLocal()
    try:
        counts = {}
        for s in sorted(ALLOWED_STATUSES):
            counts[s] = db.query(Deal).filter(Deal.status == s).count()
        total = db.query(Deal).count()
        return {"total": total, "by_status": counts}
    finally:
        db.close()

def create_app() -> FastAPI:
    app = FastAPI(title="Phase 3 - Deal Lifecycle")
    app.include_router(router)
    return app

app = create_app()
