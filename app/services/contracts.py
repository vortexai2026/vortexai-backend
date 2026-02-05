# app/services/contracts.py
from app.ai import ask_ai
from app.pdf import generate_pdf

def generate_contract(deal, contract_type):
    prompt = f"""
    Draft a {contract_type} contract.
    This is a NON-LEGAL draft.

    Deal:
    Title: {deal['title']}
    Price: {deal['price']}
    Location: {deal['location']}
    """

    text = ask_ai(prompt)

    return generate_pdf(
        title=f"{contract_type} Draft",
        content=text
    )
