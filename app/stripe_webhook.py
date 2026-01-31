from fastapi import APIRouter, Request

router = APIRouter(prefix="/stripe/webhook", tags=["stripe"])

@router.post("")
async def stripe_webhook(request: Request):
    return {"status": "received"}
