from fastapi import APIRouter, Request

router = APIRouter(prefix="/stripe", tags=["stripe"])

@router.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    return {"status": "received"}
