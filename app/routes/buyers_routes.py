from fastapi import APIRouter
from app.services.buyers import create_buyer, get_buyer, list_buyers, disable_buyer
from app.models import BuyerCreate

router = APIRouter(prefix="/buyers", tags=["buyers"])

@router.post("/create")
def create(buyer: BuyerCreate):
    return create_buyer(buyer)

@router.get("/")
def list_all():
    return list_buyers()

@router.get("/{buyer_id}")
def get_one(buyer_id: str):
    return get_buyer(buyer_id)

@router.post("/disable/{buyer_id}")
def disable(buyer_id: str):
    return disable_buyer(buyer_id)
