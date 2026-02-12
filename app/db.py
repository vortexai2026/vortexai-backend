# app/db.py
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Replace these with your database info
DB_USER = "your_user"
DB_PASS = "your_password"
DB_HOST = "localhost"
DB_NAME = "vortexai_db"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Async session
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

metadata = MetaData()

# Example table
deals = Table(
    "deals",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
)
