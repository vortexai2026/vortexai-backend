from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Your Supabase PostgreSQL connection
DATABASE_URL = "postgresql+asyncpg://postgres.msebndbsblvsslpqpprq:KBWONABclpSz5a1S@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

# Fix DuplicatePreparedStatementError with PgBouncer
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"statement_cache_size": 0}  # critical fix
)

Base = declarative_base()

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
