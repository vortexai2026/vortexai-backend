import uuid
from fastapi import APIRouter
from app.database import fetch_all, execute
from app.models import DealCreate

router = APIRouter(prefix="/deals", tags=["deals"])

@router.post("/create")
def create_deal(payload: DealCreate):
    deal_id = str(uuid.uuid4())

    execute(
        """
        INSERT INTO deals (id, title, price, location, asset_type, source)
        VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            deal_id,
            payload.title,
            payload.price,
            payload.location,
            payload.asset_type,
            payload.source,
        ),
    )

    return {"id": deal_id, "status": "created"}

@router.get("")
def list_deals():
    return fetch_all("SELECT * FROM deals ORDER BY created_at DESC")
