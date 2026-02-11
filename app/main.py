from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# === ROUTES ===
from app.routes import buyers_routes
from app.routes import deals_routes
from app.routes import contracts_routes
from app.routes import outreach_routes
from app.routes import pdf_routes
from app.routes import sources_routes
from app.routes import stripe_routes
from app.routes import ingest_routes
from app.routes import health
from app.routes import stripe_webhook


app = FastAPI(title="VortexAI Backend")


# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === ROOT + HEALTH ===
@app.get("/")
def root():
    return {"status": "VortexAI backend running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# === INCLUDE ROUTERS ===
app.include_router(buyers_routes.router)
app.include_router(deals_routes.router)
app.include_router(contracts_routes.router)
app.include_router(outreach_routes.router)
app.include_router(pdf_routes.router)
app.include_router(sources_routes.router)
app.include_router(stripe_routes.router)
app.include_router(ingest_routes.router)
app.include_router(health.router)
app.include_router(stripe_webhook.router)
