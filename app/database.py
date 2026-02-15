import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

# ==============================
# DATABASE URL
# ==============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing. Set it in Railway Variables.")

# Auto-fix if sync URL accidentally used
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1,
    )

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )

print(f"USING DATABASE URL: '{DATABASE_URL}'")

# ==============================
# ENGINE
# ==============================

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # change to True only for debugging
)

# ==============================
# SESSION MAKER
# ==============================

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ==============================
# BASE MODEL
# ==============================

Base = declarative_base()

# ==============================
# DEPENDENCY (FastAPI)
# ==============================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
