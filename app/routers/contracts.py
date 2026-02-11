from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
import base64
import pdfkit
import tempfile
import os

router = APIRouter(prefix="/contracts", tags=["contracts"])

# -----------------------------
# MODELS
# -----------------------------

class Party(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None

class ContractRequest(BaseModel):
    country: str            # "CA" or "US"
    jurisdiction: str       # Province or State
    seller: Party
    buyer: Party
    address: str
    legal_description: str | None = None
    purchase_price: float
    assignment_fee: float
    deposit_amount: float
    offer_date: date
    closing_date: date
    inspection_period_days: int = 0
    special_terms: str | None = None

class ContractResponse(BaseModel):
    purchase_agreement_pdf_b64: str
    assignment_contract_pdf_b64: str

# -----------------------------
# TEMPLATES
# -----------------------------

CANADA_PURCHASE = """<html><body>
<h1>Canadian Purchase Agreement</h1>
<p>Jurisdiction: {{jurisdiction}}</p>
<p>Seller: {{seller_name}}</p>
<p>Buyer: {{buyer_name}}</p>
<p>Address: {{address}}</p>
<p>Purchase Price: ${{purchase_price}}</p>
<p>Deposit: ${{deposit_amount}}</p>
<p>Closing Date: {{closing_date}}</p>
<p>Inspection: {{inspection_period_days}} days</p>
<p>Special Terms: {{special_terms}}</p>
</body></html>
"""

CANADA_ASSIGNMENT = """<html><body>
<h1>Canadian Assignment Contract</h1>
<p>Assignor: {{assignor_name}}</p>
<p>Assignee: {{assignee_name}}</p>
<p>Address: {{address}}</p>
<p>Assignment Fee: ${{assignment_fee}}</p>
</body></html>
"""

USA_PURCHASE = """<html><body>
<h1>US Purchase Agreement</h1>
<p>State: {{jurisdiction}}</p>
<p>Seller: {{seller_name}}</p>
<p>Buyer: {{buyer_name}}</p>
<p>Address: {{address}}</p>
<p>Purchase Price: ${{purchase_price}}</p>
<p>Deposit: ${{deposit_amount}}</p>
<p>Closing Date: {{closing_date}}</p>
<p>Inspection: {{inspection_period_days}} days</p>
<p>Special Terms: {{special_terms}}</p>
</body></html>
"""

USA_ASSIGNMENT = """<html><body>
<h1>US Assignment Contract</h1>
<p>Assignor: {{assignor_name}}</p>
<p>Assignee: {{assignee_name}}</p>
<p>Address: {{address}}</p>
<p>Assignment Fee: ${{assignment_fee}}</p>
</body></html>
"""

# -----------------------------
# HELPERS
# -----------------------------

def fill(template: str, data: dict) -> str:
    html = template
    for k, v in data.items():
        html = html.replace(f"{{{{{k}}}}}", str(v))
    return html

def html_to_pdf_b64(html: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdfkit.from_string(html, tmp.name)
        tmp.seek(0)
        pdf_bytes = tmp.read()
    os.unlink(tmp.name)
    return base64.b64encode(pdf_bytes).decode("utf-8")

# -----------------------------
# ROUTE
# -----------------------------

@router.post("/generate", response_model=ContractResponse)
def generate_contracts(payload: ContractRequest):

    data = {
        "jurisdiction": payload.jurisdiction,
        "seller_name": payload.seller.name,
        "buyer_name": payload.buyer.name,
        "assignor_name": payload.buyer.name,
        "assignee_name": payload.buyer.name,
        "address": payload.address,
        "purchase_price": payload.purchase_price,
        "assignment_fee": payload.assignment_fee,
        "deposit_amount": payload.deposit_amount,
        "closing_date": payload.closing_date,
        "inspection_period_days": payload.inspection_period_days,
        "special_terms": payload.special_terms or "",
    }

    if payload.country.upper() == "CA":
        purchase_html = fill(CANADA_PURCHASE, data)
        assignment_html = fill(CANADA_ASSIGNMENT, data)
    else:
        purchase_html = fill(USA_PURCHASE, data)
        assignment_html = fill(USA_ASSIGNMENT, data)

    purchase_pdf = html_to_pdf_b64(purchase_html)
    assignment_pdf = html_to_pdf_b64(assignment_html)

    return ContractResponse(
        purchase_agreement_pdf_b64=purchase_pdf,
        assignment_contract_pdf_b64=assignment_pdf
    )
