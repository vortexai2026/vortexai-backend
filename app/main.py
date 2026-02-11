from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your route modules
from app.routes import deals_routes
from app.routes import buyers_routes
from app.routes import outreach_routes
from app.routes import contracts_routes
from app.routes import sources_routes
from app.routes import pdf_routes
from app.routes import stripe_routes

app = FastAPI(title="VortexAI Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"status": "VortexAI backend running"}

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Register routers
app.include_router(deals_routes.router)
app.include_router(buyers_routes.router)
app.include_router(outreach_routes.router)
app.include_router(contracts_routes.router)
app.include_router(sources_routes.router)
app.include_router(pdf_routes.router)
app.include_router(stripe_routes.router)
