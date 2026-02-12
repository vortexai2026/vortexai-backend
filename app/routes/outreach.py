from fastapi import APIRouter

router = APIRouter(tags=["outreach"])

@router.get("/outreach/{buyer_id}/{deal_id}")
def generate_outreach(buyer_id: int, deal_id: int):
    return {"buyer_id": buyer_id, "deal_id": deal_id, "message": "Outreach generated"}
