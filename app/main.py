# app/main.py
from fastapi import FastAPI
from app.deals_routes import router as deals_router
from app.ai_level6_strategy import strategy_summary

app = FastAPI(title="VortexAI Backend", version="1.0")

@app.get("/")
def root():
    return {"ok": True, "service": "vortexai-backend"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/strategy")
def strategy():
    return strategy_summary()

app.include_router(deals_router)
