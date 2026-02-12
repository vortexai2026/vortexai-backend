# vortexai-backend/app/services/buyers.py

from app.db import db

def create_buyer_in_db(buyer_data: dict):
    """
    Create a new buyer in the database.
    Expects a dict with keys: name, email, asset_type, city, min_price, max_price, tier
    """
    query = """
    INSERT INTO buyers
    (name, email, asset_type, city, min_price, max_price, tier)
    VALUES
    (:name, :email, :asset_type, :city, :min_price, :max_price, :tier)
    RETURNING id;
    """
    return db.fetch_one(query, buyer_data)

def list_buyers_from_db(limit: int = 50):
    """
    List buyers from the database, with a limit.
    """
    query = """
    SELECT id, name, email, asset_type, city, min_price, max_price, tier
    FROM buyers
    ORDER BY id DESC
    LIMIT :limit;
    """
    return db.fetch_all(query, {"limit": limit})

def get_buyer_from_db(buyer_id: int):
    """
    Get a single buyer by ID.
    """
    query = """
    SELECT id, name, email, asset_type, city, min_price, max_price, tier
    FROM buyers
    WHERE id = :id;
    """
    return db.fetch_one(query, {"id": buyer_id})

def disable_buyer_in_db(buyer_id: int):
    """
    Disable a buyer by setting a 'disabled' flag (or delete if you prefer).
    Make sure your buyers table has a 'disabled' boolean column.
    """
    query = """
    UPDATE buyers
    SET disabled = TRUE
    WHERE id = :id
    RETURNING id;
    """
    return db.fetch_one(query, {"id": buyer_id})
