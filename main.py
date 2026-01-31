from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTES
from deals_routes import router as deals_router
from pdf_routes import router as pdf_router
from stripe_routes import router as stripe_router
from stripe_webhook import router as stripe_webhook_router

# OPTIONAL: AI (only include if files exist)
try:
    from ai.level1_rules import router as ai_level1
    from ai.level2_scoring_ai import router as ai_level2
    from ai.level3_decision_ai import router as ai_level3
    from ai.level4_action_ai import router as ai_level4
    from ai.level5_learning_ai import router as ai_level5
    from ai.level6_strategy_ai import router as ai_level6
except Exception:
    ai_level1 = ai_level2 = ai_level3 = None
    ai_level4 = ai_level5 = ai_level6 = None


# -------------------------
# APP INIT
# -------------------------
app = FastAPI(
    title="VortexAI Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -------------------------
# MIDDLEWARE
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# ROOT + HEALTH
# -------------------------
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

# -------------------------
# CORE ROUTES
# -------------------------
app.include_router(deals_router)
app.include_router(pdf_router)
app.include_router(stripe_router)
app.include_router(stripe_webhook_router)

# -------------------------
# AI ROUTES (SAFE LOAD)
# -------------------------
if ai_level1:
    app.include_router(ai_level1)
if ai_level2:
    app.include_router(ai_level2)
if ai_level3:
    app.include_router(ai_level3)
if ai_level4:
    app.include_router(ai_level4)
if ai_level5:
    app.include_router(ai_level5)
if ai_level6:
    app.include_router(ai_level6)

# -------------------------
# STARTUP LOG
# -------------------------
@app.on_event("startup")
def startup():
    print("🚀 VortexAI backend started successfully")
