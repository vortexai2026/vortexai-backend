from fastapi import APIRouter
from .buyers import router as buyers_router
from .deals import router as deals_router

router = APIRouter()

router.include_router(buyers_router, prefix="/buyers", tags=["Buyers"])
router.include_router(deals_router, prefix="/deals", tags=["Deals"])
