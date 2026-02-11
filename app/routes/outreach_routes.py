from fastapi import APIRouter, HTTPException
from app.services.outreach_generator import generate_outreach_message
from app.database import fetch_one

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.get("/{buyer_id}/{deal_id}")
def generate_outreach(buyer_id: str, deal_id: str):
    buyer = fetch_one("SELECT * FROM buyers WHERE id=%s", (buyer_id,))
    deal = fetch_one("SELECT * FROM deals WHERE id=%s", (deal_id,))

    if not buyer or not deal:
        raise HTTPException(status_code=404, detail="Buyer or deal not found")

    message = generate_outreach_message(dict(buyer), dict(deal))
    return {"message": message}
