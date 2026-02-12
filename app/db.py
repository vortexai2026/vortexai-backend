import os
import sqlalchemy
import databases

# Database URL (adjust if needed)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/vortexai"
)

# Connect to database
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Example table
deals = sqlalchemy.Table(
    "deals",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("price", sqlalchemy.Float, nullable=False),
)
