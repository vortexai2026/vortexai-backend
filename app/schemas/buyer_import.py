from pydantic import BaseModel


class BuyerImport(BaseModel):
    name: str
    email: str
    phone: str | None = None
    market_tag: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    buy_box_beds: int | None = None
    buy_box_baths: float | None = None
    proof_of_funds: str | None = None
    notes: str | None = None
