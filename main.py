from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pdf_routes import router as pdf_router
from stripe_routes import router as stripe_router
from stripe_webhook import router as stripe_webhook_router

app = FastAPI(
    title="VortexAI Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "VortexAI",
        "message": "Backend running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(pdf_router)
app.include_router(stripe_router)
app.include_router(stripe_webhook_router)
