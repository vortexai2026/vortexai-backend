import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.services.automation_worker import run_once

# 🔥 Register ONLY existing models (NO CAR)
import app.models.deal
import app.models.buyer
import app.models.followup
import app.models.seller_call
import app.models.buyer_interest
import app.models.buyer_outreach_log
import app.models.ai_decision_log

# ROUTES
from app.routes import (
    deals,
    buyers,
    ingest,
    offers,
    buyer_blast,
    assignment,
    stripe_webhook,
    autonomous
)

app = FastAPI(title="Vortex AI Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(ingest.router)
app.include_router(deals.router)
app.include_router(buyers.router)
app.include_router(offers.router)
app.include_router(buyer_blast.router)
app.include_router(assignment.router)
app.include_router(stripe_webhook.router)
app.include_router(autonomous.router)


@app.on_event("startup")
async def startup_event():
    print("USING DATABASE URL:", os.getenv("DATABASE_URL"))

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tables created & DB ready")

    auto_run = os.getenv("AUTO_RUN_ON_STARTUP", "false").lower() == "true"

    if auto_run:
        print("🤖 Autonomous mode starting...")
        asyncio.create_task(run_once())
        print("🤖 Autonomous worker started")


@app.get("/")
async def root():
    return {
        "message": "Vortex AI Execution Engine Running",
        "mode": "Wholesale Autonomous Backend"
    }
