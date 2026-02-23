# app/main.py
from fastapi import FastAPI

from app.routes.deals import router as deals_router
from app.routes.autonomous import router as autonomous_router

app = FastAPI(title="Vortex AI Backend", version="2.0")

app.include_router(deals_router)
app.include_router(autonomous_router)

@app.get("/")
def root():
    return {"status": "ok"}
