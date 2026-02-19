from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from app.database import get_db
from app.models.car import CarInventory, CarLead, CarMessage, CarSale
from app.schemas.car import CarCreate, CarOut, LeadCreate, LeadOut, MessageCreate, SaleCreate
from app.services.brevo_sms import BrevoSMS

router = APIRouter(prefix="/cars", tags=["Cars"])

@router.post("/inventory", response_model=CarOut)
async def create_car(payload: CarCreate, db: AsyncSession = Depends(get_db)):
    car = CarInventory(**payload.model_dump())
    db.add(car)
    await db.commit()
    await db.refresh(car)
    return car

@router.get("/inventory", response_model=list[CarOut])
async def list_cars(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CarInventory).order_by(CarInventory.created_at.desc()))
    return list(res.scalars().all())

@router.post("/leads", response_model=LeadOut)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    lead = CarLead(**payload.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead

@router.get("/leads", response_model=list[LeadOut])
async def list_leads(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CarLead).order_by(CarLead.created_at.desc()))
    return list(res.scalars().all())

@router.post("/messages")
async def log_message(payload: MessageCreate, db: AsyncSession = Depends(get_db)):
    msg = CarMessage(**payload.model_dump())
    db.add(msg)
    await db.commit()
    return {"ok": True}

@router.post("/sales")
async def record_sale(payload: SaleCreate, db: AsyncSession = Depends(get_db)):
    sale = CarSale(**payload.model_dump())
    db.add(sale)
    # mark car sold
    await db.execute(update(CarInventory).where(CarInventory.id == payload.car_id).values(status="sold"))
    await db.commit()
    return {"ok": True}

@router.post("/leads/{lead_id}/sms")
async def sms_lead(lead_id: UUID, text: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CarLead).where(CarLead.id == lead_id))
    lead = res.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")
    if not lead.phone:
        raise HTTPException(400, "Lead has no phone")

    # NOTE: You must pass E.164 like +12045551234
    send_res = await BrevoSMS.send_sms(lead.phone, text)

    db.add(CarMessage(lead_id=lead.id, direction="outbound", message=text))
    await db.commit()

    return {"sent": True, "brevo": send_res}
