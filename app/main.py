# app/main.py

from fastapi import FastAPI, BackgroundTasks

# Core routes
from app.deals_routes import router as deals_router

# Ingestion (manual / VA safe)
from app.routes.ingest_routes import router as ingest_router

# Strategy / AI
from app.ai_level6_strategy import strategy_summary

# Ops / reporting
from app.ai_daily_report_sender import send_daily_report

app = FastAPI(
    title="VortexAI Backend",
    version="1.0"
)

# -------------------------
# BASIC HEALTH / INFO
# -------------------------

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "vortexai-backend",
        "mode": "operator"
    }

@app.get("/health")
def health():
    return {"ok": True}

# -------------------------
# AI STRATEGY
# -------------------------

@app.get("/strategy")
def strategy():
    return strategy_summary()

# -------------------------
# ADMIN / OPS
# -------------------------
# Can be called by:
# - Railway cron
# - External cron
# - Manual trigger
# (Protect later if needed)

@app.post("/admin/run-daily-report")
def run_daily_report(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_daily_report)
    return {
        "ok": True,
        "status": "daily report scheduled"
    }

# -------------------------
# ROUTERS
# -------------------------

app.include_router(deals_router)
app.include_router(ingest_router)
