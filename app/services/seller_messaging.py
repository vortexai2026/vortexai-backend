from datetime import datetime
from app.models.deal import Deal

async def generate_initial_message(deal: Deal) -> str:
    return (
        f"Hi, I'm looking to buy properties in {deal.city}. "
        f"Would you consider an offer on {deal.address}?"
    )

async def register_contact_attempt(deal: Deal):
    deal.contact_attempts = (deal.contact_attempts or 0) + 1
    deal.last_contacted_at = datetime.utcnow()
