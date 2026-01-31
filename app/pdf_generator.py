from fastapi import APIRouter

router = APIRouter(prefix="/stripe", tags=["stripe"])

@router.get("/status")
def stripe_status():
    return {"stripe": "ok"}
