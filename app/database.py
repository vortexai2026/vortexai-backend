import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL missing!")

# Make sure the URL has asyncpg prefix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# SSL context for Supabase
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE  # Supabase allows this

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}  # pass SSL config here
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
