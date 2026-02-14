from fastapi import APIRouter

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.get("/plans")
async def get_plans():
    return {
        "plans": [
            {"name": "Free", "price": 49},
            {"name": "Pro", "price": 199},
            {"name": "Elite", "price": 499},
        ]
    }
