from fastapi import APIRouter

router = APIRouter(prefix="/buyers", tags=["Buyers"])

@router.get("/")
async def list_buyers():
    return {"message": "Buyers endpoint working"}

@router.post("/create")
async def create_buyer(data: dict):
    return {"message": "Buyer created", "data": data}
