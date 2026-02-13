from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:<PASSWORD>@<HOST>:<PORT>/<DBNAME>"

# Disable asyncpg prepared statement cache to avoid DuplicatePreparedStatementError
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # optional: shows SQL logs
    connect_args={"statement_cache_size": 0},
)

# Async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()
