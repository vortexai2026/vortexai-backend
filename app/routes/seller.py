from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.seller_lead import SellerLead
from app.models.deal import Deal
from app.schemas.seller import SellerIntakeIn

router = APIRouter(prefix="/seller", tags=["Seller"])

@router.post("/intake")
async def seller_intake(payload: SellerIntakeIn, session: AsyncSession = Depends(get_session)):
    lead = SellerLead(**payload.model_dump())
    session.add(lead)
    await session.commit()
    await session.refresh(lead)

    # auto-create deal
    deal = Deal(
        seller_lead_id=lead.id,
        property_address=lead.property_address,
        city=lead.city,
        state=lead.state,
        zip=lead.zip,
        status="NEW",
    )
    session.add(deal)
    await session.commit()
    await session.refresh(deal)

    return {"ok": True, "seller_lead_id": lead.id, "deal_id": deal.id}
