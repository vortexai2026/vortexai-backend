# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routes import (
    buyers_routes,
    deals_routes,
    contracts_routes,
    ingest_routes,
    outreach_routes,
    pdf_routes,
    sources_routes,
    stripe_routes
)

app = FastAPI(
    title="VortexAI Backend",
    version="0.1.0",
    description="Backend API for VortexAI platform"
)

# Allow all CORS requests (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {"ok": True, "message": "VortexAI Backend is running!"}

# Health endpoint
@app.get("/health", tags=["Health"])
def health():
    return {"ok": True, "status": "healthy"}

# Include routers with **prefixes here only**
app.include_router(buyers_routes.router, prefix="/buyers")
app.include_router(deals_routes.router, prefix="/deals")
app.include_router(contracts_routes.router, prefix="/contracts")
app.include_router(ingest_routes.router, prefix="/ingest")
app.include_router(outreach_routes.router, prefix="/outreach")
app.include_router(pdf_routes.router, prefix="/pdf")
app.include_router(sources_routes.router, prefix="/sources")
app.include_router(stripe_routes.router, prefix="/stripe")

# Startup / shutdown events
@app.on_event("startup")
async def startup_event():
    print("VortexAI Backend starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    print("VortexAI Backend shutting down...")
