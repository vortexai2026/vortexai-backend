import databases
import sqlalchemy
import os

# Load env variables if you want
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/vortexai"
)

# Database connection
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Example table (optional)
deals = sqlalchemy.Table(
    "deals",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("price", sqlalchemy.Float, nullable=False),
)
