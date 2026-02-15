from sqlalchemy import select
from app.models.deal import Deal
from datetime import datetime

# ... inside log_call() before commit:
deal_res = await db.execute(select(Deal).where(Deal.id == deal_id))
deal = deal_res.scalar_one_or_none()
if deal:
    deal.last_contacted_at = datetime.utcnow()
