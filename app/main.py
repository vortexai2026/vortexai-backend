from fastapi import FastAPI
from app.db import database, metadata, deals
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VortexAI Backend")

# Allow all CORS (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup / shutdown events
@app.on_event("startup")
async def startup_event():
    await database.connect()
    # Create tables if not exist
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Example route
@app.get("/deals")
async def get_deals():
    query = deals.select()
    return await database.fetch_all(query)
