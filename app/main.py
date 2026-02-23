from fastapi import FastAPI
from app.routes.seller import router as seller_router
from app.routes.deals import router as deals_router
from app.routes.buyers import router as buyers_router
from app.routes.deal_room import router as deal_room_router

app = FastAPI(title="Vortex AI Deal Control", version="1.0.0")

app.include_router(seller_router)
app.include_router(deals_router)
app.include_router(buyers_router)
app.include_router(deal_room_router)

@app.get("/")
def root():
    return {"ok": True, "service": "Vortex AI Deal Control"}
