# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, metadata

# Import your routers
# from app.routes import buyers, deals, contracts, ingest, outreach, pdf, sources, stripe

app = FastAPI(title="VortexAI Backend")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    print("Database connected and tables created!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()
    print("Database connection closed!")

# Example root endpoint
@app.get("/")
async def root():
    return {"message": "VortexAI Backend is running!"}

# Include routers here
# app.include_router(buyers.router, prefix="/buyers", tags=["buyers"])
# app.include_router(deals.router, prefix="/deals", tags=["deals"])
# app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
# app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
# app.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
# app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
# app.include_router(sources.router, prefix="/sources", tags=["sources"])
# app.include_router(stripe.router, prefix="/stripe", tags=["stripe"])

