import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL missing in .env")

# Ensure proper asyncpg URL format
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,              # Optional: limit connections
    max_overflow=10,          # Optional: allow extra connections
    connect_args={
        "statement_cache_size": 0  # ✅ DISABLE prepared statements for PgBouncer
    },
)

# Session maker
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session
