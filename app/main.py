# app/main.py
from fastapi import FastAPI
from app.deals_routes import router as deals_router
from app.outreach_routes import router as outreach_router
from app.ai_level6_strategy import strategy_summary

# Optional ingest routes
try:
    from app.ingest_routes import router as ingest_router
except Exception:
    ingest_router = None

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

# Routers
app.include_router(deals_router)
app.include_router(outreach_router)

if ingest_router:
    app.include_router(ingest_router)
