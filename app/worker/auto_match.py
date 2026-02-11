import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Buyer, Deal
from emailer import send_email

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

def auto_match():
    db = Session()

    deals = db.query(Deal).filter(Deal.status == "new").all()
    buyers = db.query(Buyer).filter(Buyer.tier != "free").all()

    for deal in deals:
        for buyer in buyers:
            if (
                deal.asset_type.lower() == buyer.asset_type.lower()
                and buyer.location.lower() in deal.location.lower()
            ):
                deal.status = "matched"
                deal.matched_buyer_id = buyer.id

                send_email(
                    buyer.email,
                    "🔥 New Deal Matched for You",
                    f"""
                    <h2>{deal.title}</h2>
                    <p>Location: {deal.location}</p>
                    <p>Price: {deal.price}</p>
                    """
                )

                db.commit()
                break

    db.close()

