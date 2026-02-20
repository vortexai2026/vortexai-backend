from .deals import router as deals_router
from .buyers import router as buyers_router
from .autonomous import router as autonomous_router

__all__ = ["deals_router", "buyers_router", "autonomous_router"]
