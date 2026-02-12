# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers from each route file
from app.routes.buyers_routes import router as buyers_router
from app.routes.deals_routes import router as deals_router
from app.routes.contracts_routes import router as contracts_router
from app.routes.outreach_routes import router as outreach_router
from app.routes.pdf_routes import router as pdf_router
from app.routes.sources_routes import router as sources_router
from app.routes.stripe_routes import router as stripe_router
from app.routes.ingest_routes import router as ingest_router
from app.routes.health import router as health_router
from app.routes.stripe_webhook import router as stripe_webhook_router

# Initialize FastAPI app
app = FastAPI(title="VortexAI Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your domains later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic root endpoint
@app.get("/")
def root():
    return {"status": "VortexAI backend running"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include all routers
app.include_router(buyers_router)
app.include_router(deals_router)
app.include_router(contracts_router)
app.include_router(outreach_router)
app.include_router(pdf_router)
app.include_router(sources_router)
app.include_router(stripe_router)
app.include_router(ingest_router)
app.include_router(health_router)
app.include_router(stripe_webhook_router)
