# app/ai_outreach_writer.py

def build_outreach_message(deal: dict) -> str:
    """
    Temporary outreach message builder.
    Replace with AI logic later.
    """
    title = deal.get("title", "New Deal")
    price = deal.get("price", "N/A")
    location = deal.get("location", "Unknown")

    return (
        f"🔥 New Opportunity!\n"
        f"Title: {title}\n"
        f"Price: {price}\n"
        f"Location: {location}\n"
        f"Reply if interested."
    )
