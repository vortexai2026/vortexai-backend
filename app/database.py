from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:YOUR_PASSWORD@YOUR_HOST:5432/YOUR_DB"

# Create async engine (disable statement cache for PgBouncer transaction mode)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"statement_cache_size": 0}  # fixes DuplicatePreparedStatementError
)

# Async session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()
