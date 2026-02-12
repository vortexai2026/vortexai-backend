from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all route modules
from app.routes import (
    buyers_routes,
    contracts_routes,
    deals_routes,
    ingest_routes,
    outreach_routes,
    pdf_routes,
    sources_routes,
    stripe_routes
)

app = FastAPI(title="VortexAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "VortexAI backend running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Register all routers
app.include_router(buyers_routes.router)
app.include_router(contracts_routes.router)
app.include_router(deals_routes.router)
app.include_router(ingest_routes.router)
app.include_router(outreach_routes.router)
app.include_router(pdf_routes.router)
app.include_router(sources_routes.router)
app.include_router(stripe_routes.router)
