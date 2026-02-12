from fastapi import FastAPI
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

app = FastAPI()

@app.get("/")
def root():
    return {"message": "VortexAI API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Register all routes
app.include_router(buyers_routes.router)
app.include_router(contracts_routes.router)
app.include_router(deals_routes.router)
app.include_router(ingest_routes.router)
app.include_router(outreach_routes.router)
app.include_router(pdf_routes.router)
app.include_router(sources_routes.router)
app.include_router(stripe_routes.router)
