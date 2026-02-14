from fastapi import APIRouter

router = APIRouter(prefix="/deals", tags=["Deals"])

@router.get("/")
async def list_deals():
    return {"message": "Deals endpoint working"}

@router.post("/create")
async def create_deal(data: dict):
    return {"message": "Deal created", "data": data}
