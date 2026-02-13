# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres.msebndbsblvsslpqpprq:KBWONABclpSz5a1S@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
)

# Create async engine with statement_cache_size=0 for PgBouncer
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"statement_cache_size": 0}  # <--- THIS FIXES DuplicatePreparedStatementError
)

# Async session factory
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI endpoints
async def get_db():
    async with async_session() as session:
        yield session
