from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTES
from deals_routes import router as deals_router

app = FastAPI(
    title="VortexAI Backend",
    version="1.0.0"
)

# -----------------------------
# CORS (OPEN FOR NOW)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# BASIC HEALTH ROUTES
# -----------------------------
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

# -----------------------------
# REGISTER ROUTES
# -----------------------------
app.include_router(deals_router)
