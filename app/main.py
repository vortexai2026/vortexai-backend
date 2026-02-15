# app/main.py

import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.worker.autonomous_worker import run_once

# ROUTES
from app.routes import (
    deals,
    buyers,
    ingest,
    lifecycle,
    seller_calls,
    offers,
    buyer_blast,
    assignment,
    payments,
    stripe_webhook,
    deal_room,
    operator_dashboard,
    autonomous
)

app = FastAPI(title="Vortex AI Backend", version="1.0.0")

# CORS (allow frontend if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Core Routes
app.include_router(ingest.router)
app.include_router(deals.router)
app.include_router(buyers.router)
app.include_router(lifecycle.router)

# Execution Layer
app.include_router(seller_calls.router)
app.include_router(offers.router)
app.include_router(buyer_blast.router)
app.include_router(assignment.router)

# Payments
app.include_router(payments.router)
app.include_router(stripe_webhook.router)

# Deal Room
app.include_router(deal_room.router)

# Operator Metrics
app.include_router(operator_dashboard.router)

# Autonomous Engine
app.include_router(autonomous.router)


@app.on_event("startup")
async def startup_event():
    """
    Runs when container starts.
    Creates tables and optionally runs autonomous cycle.
    """
    print("USING DATABASE URL:", os.getenv("DATABASE_URL"))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tables created & DB ready")

    # Optional autonomous run on startup
    auto_run = os.getenv("AUTO_RUN_ON_STARTUP", "false").lower() == "true"

    if auto_run:
        print("🤖 Autonomous mode starting...")
        try:
            await run_once()
            print("🤖 Autonomous cycle complete")
        except Exception as e:
            print("❌ Autonomous error:", str(e))


@app.get("/")
async def root():
    return {
        "message": "Vortex AI Execution Engine Running",
        "mode": "Wholesale Autonomous Backend"
    }
