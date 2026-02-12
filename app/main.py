# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers (match your new filenames)
from app.routes import (
    buyers,
    deals,
    contracts,
    ingest,
    outreach,
    pdf,
    sources,
    stripe
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

# Include routers
app.include_router(buyers.router, prefix="/buyers")
app.include_router(deals.router, prefix="/deals")
app.include_router(contracts.router, prefix="/contracts")
app.include_router(ingest.router, prefix="/ingest")
app.include_router(outreach.router, prefix="/outreach")
app.include_router(pdf.router, prefix="/pdf")
app.include_router(sources.router, prefix="/sources")
app.include_router(stripe.router, prefix="/stripe")

# Startup / shutdown events
@app.on_event("startup")
async def startup_event():
    print("VortexAI Backend starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    print("VortexAI Backend shutting down...")
