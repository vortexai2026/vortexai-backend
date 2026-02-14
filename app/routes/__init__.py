from fastapi import APIRouter
from .buyers import router as buyers_router
from .billing import router as billing_router

router = APIRouter()
router.include_router(buyers_router)
router.include_router(billing_router)
