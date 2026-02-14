import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing.")

# 🔥 HARD CLEAN — removes spaces, tabs, newlines
DATABASE_URL = DATABASE_URL.strip().replace("\n", "").replace("\r", "")

# 🔥 Force async driver even if Railway injects normal URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

print("USING DATABASE URL:", repr(DATABASE_URL))

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

Base = declarative_base()

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with async_session() as session:
        yield session
