# app/routes/__init__.py
from .deals import router as deals_router
from .autonomous import router as autonomous_router

__all__ = ["deals_router", "autonomous_router"]
