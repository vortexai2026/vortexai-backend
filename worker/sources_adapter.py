from fastapi import FastAPI
from app.deals_routes import router as deals_router
from app.outreach_routes import router as outreach_router
from app.sources_routes import router as sources_router
from app.contracts_routes import router as contracts_router

app = FastAPI(title="VortexAI Backend", version="1.0")

@app.get("/")
def root():
    return {"ok": True, "service": "vortexai-backend"}

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(deals_router)
app.include_router(outreach_router)
app.include_router(sources_router)
app.include_router(contracts_router)

