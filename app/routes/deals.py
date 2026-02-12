from fastapi import APIRouter

router = APIRouter(tags=["deals"])

@router.post("/deals/create")
def create_deal():
    return {"message": "Deal created"}

@router.get("/deals")
def list_deals():
    return {"deals": []}

@router.get("/deals/{deal_id}")
def get_deal(deal_id: int):
    return {"deal_id": deal_id}

@router.get("/deals/match/{deal_id}")
def match_buyers(deal_id: int):
    return {"deal_id": deal_id, "matched_buyers": []}
