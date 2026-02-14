from datetime import datetime

def generate_assignment_contract(deal, buyer):

    assignment_fee = deal.assignment_fee or 15000
    contract_price = deal.offer_sent_price or 0
    total_due = contract_price + assignment_fee

    template_data = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "buyer_name": buyer.name,
        "property_address": deal.title,
        "contract_price": contract_price,
        "assignment_fee": assignment_fee,
        "total_due": total_due,
        "closing_date": "TBD"
    }

    return template_data
