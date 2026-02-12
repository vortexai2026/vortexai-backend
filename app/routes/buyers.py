# app/routes/buyers.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import fetch_all, fetch_one, execute  # fixed import

router = APIRouter(tags=["buyers"])

# Pydantic model for creating a buyer
class BuyerCreate(BaseModel):
    name: str
    email: str
    asset_type: str
    city: str
    min_price: float
    max_price: float
    tier: str = "free"

# Create a new buyer
@router.post("/create")
def create_buyer(buyer: BuyerCreate):
    query = """
    INSERT INTO buyers
    (name, email, asset_type, city, min_price, max_price, tier)
    VALUES
    (%(name)s, %(email)s, %(asset_type)s, %(city)s, %(min_price)s, %(max_price)s, %(tier)s)
    RETURNING id;
    """
    try:
        new_id = fetch_one(query, buyer.dict())
        return {"id": new_id["id"], "message": "Buyer created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"create_buyer failed: {str(e)}")

# List all buyers
@router.get("/")
def list_buyers():
    query = "SELECT * FROM buyers;"
    return fetch_all(query)

# Get a single buyer
@router.get("/{buyer_id}")
def get_buyer(buyer_id: int):
    query = "SELECT * FROM buyers WHERE id = %(id)s;"
    buyer = fetch_one(query, {"id": buyer_id})
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return buyer

# Disable a buyer
@router.post("/disable/{buyer_id}")
def disable_buyer(buyer_id: int):
    query = "UPDATE buyers SET active = FALSE WHERE id = %(id)s RETURNING id;"
    result = fetch_one(query, {"id": buyer_id})
    if not result:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return {"id": result["id"], "message": "Buyer disabled successfully"}
