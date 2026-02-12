# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
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

# Optional: Allow all CORS requests (needed if your frontend is separate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or list of your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {"ok": True, "message": "VortexAI Backend is running!"}

# Health check endpoint
@app.get("/health", tags=["Health"])
def health():
    return {"ok": True, "status": "healthy"}

# Include all routers with proper prefixes and tags
app.include_router(buyers_routes.router, prefix="/buyers", tags=["Buyers"])
app.include_router(deals_routes.router, prefix="/deals", tags=["Deals"])
app.include_router(contracts_routes.router, prefix="/contracts", tags=["Contracts"])
app.include_router(ingest_routes.router, prefix="/ingest", tags=["Ingest"])
app.include_router(outreach_routes.router, prefix="/outreach", tags=["Outreach"])
app.include_router(pdf_routes.router, prefix="/pdf", tags=["PDF"])
app.include_router(sources_routes.router, prefix="/sources", tags=["Sources"])
app.include_router(stripe_routes.router, prefix="/stripe", tags=["Stripe"])

# Optional: Startup event
@app.on_event("startup")
async def startup_event():
    print("VortexAI Backend starting up...")

# Optional: Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("VortexAI Backend shutting down...")
