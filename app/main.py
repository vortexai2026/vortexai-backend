import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# =========================================
# LOAD ENV
# =========================================
load_dotenv()

# =========================================
# FASTAPI APP
# =========================================
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

# =========================================
# BASIC ROUTES
# =========================================
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

# =========================================
# IMPORT ROUTERS (CORRECT PATHS)
# =========================================
from app.api.pdf_routes import router as pdf_router
from app.api.stripe_routes import router as stripe_router
from app.api.stripe_webhook import router as stripe_webhook_router

# =========================================
# REGISTER ROUTERS
# =========================================
app.include_router(pdf_router)
app.include_router(stripe_router)
app.include_router(stripe_webhook_router)
