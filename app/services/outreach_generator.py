from typing import Dict


def generate_outreach_message(buyer: Dict, deal: Dict) -> str:
    """
    Generates a simple outreach message connecting a buyer to a deal.
    You can expand this later with AI or templates.
    """

    buyer_name = buyer.get("name", "there")
    asset_type = deal.get("asset_type", "an opportunity")
    title = deal.get("title", "a deal")
    location = deal.get("location", "the market")
    price = deal.get("price", "N/A")

    message = (
        f"Hi {buyer_name},\n\n"
        f"We found a new {asset_type} that may match your criteria:\n\n"
        f"Title: {title}\n"
        f"Location: {location}\n"
        f"Price: {price}\n\n"
        f"Let us know if you'd like more details or want to move forward.\n\n"
        f"Best,\n"
        f"VortexAI Team"
    )

    return message
