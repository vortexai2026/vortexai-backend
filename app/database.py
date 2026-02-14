import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔐 Use custom variable so Railway does NOT override it
DATABASE_URL = os.getenv("APP_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("APP_DATABASE_URL is missing. Set it in Railway Variables.")

# 🔎 Remove hidden whitespace/newlines just in case
DATABASE_URL = DATABASE_URL.strip()

print("✅ USING DATABASE URL:", repr(DATABASE_URL))

# 🚀 Async Engine (correct for asyncpg)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # Set True only for debugging
    pool_pre_ping=True,
)

Base = declarative_base()

# 🧠 Async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 📦 Dependency for FastAPI routes
async def get_db():
    async with async_session() as session:
        yield session
