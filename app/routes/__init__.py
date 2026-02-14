from fastapi import APIRouter

from .ingest import router as ingest_router
from .buyers import router as buyers_router
from .deals import router as deals_router
from .billing import router as billing_router
from .outreach import router as outreach_router
from .sources import router as sources_router
from .stripe import router as stripe_router
from .pdf import router as pdf_router
from .contracts import router as contracts_router
from .ai_pipeline import router as ai_pipeline_router
from .lifecycle import router as lifecycle_router

router = APIRouter()

router.include_router(ingest_router)
router.include_router(buyers_router)
router.include_router(deals_router)
router.include_router(billing_router)
router.include_router(outreach_router)
router.include_router(sources_router)
router.include_router(stripe_router)
router.include_router(pdf_router)
router.include_router(contracts_router)
router.include_router(ai_pipeline_router)
router.include_router(lifecycle_router)
