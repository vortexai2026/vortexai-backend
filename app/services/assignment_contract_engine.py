from datetime import datetime


def generate_assignment_contract(deal, buyer):
    """
    Generates a simple assignment contract preview.
    This is a basic version. You can expand it later.
    """

    contract_text = f"""
ASSIGNMENT OF CONTRACT AGREEMENT
---------------------------------------------

Date: {datetime.utcnow().strftime('%Y-%m-%d')}

Assignor (Wholesaler): Vortex AI
Assignee (Buyer): {getattr(buyer, 'name', 'N/A')}

Property Address:
{getattr(deal, 'address', 'N/A')}, {getattr(deal, 'city', '')}, {getattr(deal, 'state', '')}

Original Purchase Price: ${getattr(deal, 'seller_price', 0)}
Assignment Fee: ${getattr(deal, 'assignment_fee', 15000)}

The Assignor hereby assigns all rights and interest in the above referenced
purchase agreement to the Assignee.

The Assignee agrees to close on the property under the original agreement terms.

Signed:

__________________________
Assignor

__________________________
Assignee

---------------------------------------------
This is a system-generated preview.
"""

    return contract_text
