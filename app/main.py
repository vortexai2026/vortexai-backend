from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import date
import base64
import pdfkit  # wkhtmltopdf must be installed in your image
import os
import tempfile

app = FastAPI(title="Contract Generator")

class Party(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ContractRequest(BaseModel):
    country: str              # "CA" or "US"
    jurisdiction: str         # e.g. "Ontario", "Texas"
    seller: Party
    buyer: Party
    address: str
    legal_description: Optional[str] = None
    purchase_price: float
    assignment_fee: float
    deposit_amount: float
    offer_date: date
    closing_date: date
    inspection_period_days: int = 0
    special_terms: Optional[str] = None

class ContractResponse(BaseModel):
    purchase_agreement_pdf_b64: str
    assignment_contract_pdf_b64: str

# ---------- TEMPLATES ----------

CANADA_PURCHASE_TEMPLATE = """
<html>
  <body>
    <h1>Residential Purchase Agreement (Canada)</h1>
    <p><strong>Jurisdiction:</strong> {{jurisdiction}}</p>
    <p><strong>Seller:</strong> {{seller_name}}</p>
    <p><strong>Buyer:</strong> {{buyer_name}}</p>
    <p><strong>Property Address:</strong> {{address}}</p>
    <p><strong>Legal Description:</strong> {{legal_description}}</p>
    <p><strong>Purchase Price:</strong> ${{purchase_price}}</p>
    <p><strong>Deposit:</strong> ${{deposit_amount}}</p>
    <p><strong>Offer Date:</strong> {{offer_date}}</p>
    <p><strong>Closing Date:</strong> {{closing_date}}</p>
    <p><strong>Inspection Period:</strong> {{inspection_period_days}} days</p>

    <h2>Key Terms</h2>
    <p>
      The Buyer agrees to purchase and the Seller agrees to sell the Property
      described above, subject to the terms and conditions of this Agreement.
    </p>

    <p>
      This Agreement is intended to be assignable by the Buyer unless expressly
      prohibited by applicable law or by additional written terms.
    </p>

    <h3>Special Terms</h3>
    <p>{{special_terms}}</p>

    <h3>Governing Law</h3>
    <p>
      This Agreement shall be governed by the laws of {{jurisdiction}}, Canada.
    </p>

    <br><br>
    <p>Seller: ___________________________   Date: __________________</p>
    <p>Buyer:  ___________________________   Date: __________________</p>
  </body>
</html>
"""

CANADA_ASSIGNMENT_TEMPLATE = """
<html>
  <body>
    <h1>Assignment of Purchase Agreement (Canada)</h1>
    <p><strong>Jurisdiction:</strong> {{jurisdiction}}</p>
    <p><strong>Original Seller:</strong> {{seller_name}}</p>
    <p><strong>Assignor (Original Buyer):</strong> {{assignor_name}}</p>
    <p><strong>Assignee (New Buyer):</strong> {{assignee_name}}</p>
    <p><strong>Property Address:</strong> {{address}}</p>
    <p><strong>Assignment Fee:</strong> ${{assignment_fee}}</p>

    <h2>Recitals</h2>
    <p>
      The Assignor has entered into a Purchase Agreement with the Seller
      for the Property described above (the "Purchase Agreement").
      The Assignor wishes to assign all of its rights, title, and interest
      in the Purchase Agreement to the Assignee.
    </p>

    <h2>Assignment</h2>
    <p>
      In consideration of the Assignment Fee, the Assignor hereby assigns
      to the Assignee all of its rights and obligations under the Purchase
      Agreement, subject to the terms of that Agreement and applicable law.
    </p>

    <h3>Governing Law</h3>
    <p>
      This Assignment shall be governed by the laws of {{jurisdiction}}, Canada.
    </p>

    <br><br>
    <p>Seller:   ___________________________   Date: __________________</p>
    <p>Assignor: ___________________________   Date: __________________</p>
    <p>Assignee: ___________________________   Date: __________________</p>
  </body>
</html>
"""

USA_PURCHASE_TEMPLATE = """
<html>
  <body>
    <h1>Residential Purchase Agreement (USA)</h1>
    <p><strong>State:</strong> {{jurisdiction}}</p>
    <p><strong>Seller:</strong> {{seller_name}}</p>
    <p><strong>Buyer:</strong> {{buyer_name}}</p>
    <p><strong>Property Address:</strong> {{address}}</p>
    <p><strong>Legal Description:</strong> {{legal_description}}</p>
    <p><strong>Purchase Price:</strong> ${{purchase_price}}</p>
    <p><strong>Earnest Money Deposit:</strong> ${{deposit_amount}}</p>
    <p><strong>Offer Date:</strong> {{offer_date}}</p>
    <p><strong>Closing Date:</strong> {{closing_date}}</p>
    <p><strong>Inspection Period:</strong> {{inspection_period_days}} days</p>

    <h2>Key Terms</h2>
    <p>
      Buyer agrees to purchase and Seller agrees to sell the Property
      under the terms of this Agreement.
    </p>

    <p>
      Unless prohibited by state law or additional written terms,
      this Agreement may be assigned by Buyer.
    </p>

    <h3>Special Terms</h3>
    <p>{{special_terms}}</p>

    <h3>Governing Law</h3>
    <p>
      This Agreement shall be governed by the laws of the State of {{jurisdiction}}.
    </p>

    <br><br>
    <p>Seller: ___________________________   Date: __________________</p>
    <p>Buyer:  ___________________________   Date: __________________</p>
  </body>
</html>
"""

USA_ASSIGNMENT_TEMPLATE = """
<html>
  <body>
    <h1>Assignment of Purchase Agreement (USA)</h1>
    <p><strong>State:</strong> {{jurisdiction}}</p>
    <p><strong>Original Seller:</strong> {{seller_name}}</p>
    <p><strong>Assignor (Original Buyer):</strong> {{assignor_name}}</p>
    <p><strong>Assignee (New Buyer):</strong> {{assignee_name}}</p>
    <p><strong>Property Address:</strong> {{address}}</p>
    <p><strong>Assignment Fee:</strong> ${{assignment_fee}}</p>

    <h2>Recitals</h2>
    <p>
      Assignor has entered into a Purchase Agreement with Seller for the Property.
      Assignor desires to assign its rights and obligations under that Agreement
      to Assignee in exchange for the Assignment Fee.
    </p>

    <h2>Assignment</h2>
    <p>
      Assignor hereby assigns to Assignee all of Assignor's rights, title,
      and interest in and to the Purchase Agreement, subject to its terms
      and applicable state law.
    </p>

    <h3>Governing Law</h3>
    <p>
      This Assignment shall be governed by the laws of the State of {{jurisdiction}}.
    </p>

    <br><br>
    <p>Seller:   ___________________________   Date: __________________</p>
    <p>Assignor: ___________________________   Date: __________________</p>
    <p>Assignee: ___________________________   Date: __________________</p>
  </body>
</html>
"""

# ---------- HELPER FUNCTIONS ----------

def fill_template(template: str, data: dict) -> str:
    html = template
    for key, value in data.items():
        html = html.replace(f"{{{{{key}}}}}", str(value if value is not None else ""))
    return html

def html_to_pdf_b64(html: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdfkit.from_string(html, tmp.name)
        tmp.seek(0)
        pdf_bytes = tmp.read()
    os.unlink(tmp.name)
    return base64.b64encode(pdf_bytes).decode("utf-8")

# ---------- ROUTES ----------

@app.post("/contracts/generate", response_model=ContractResponse)
def generate_contracts(payload: ContractRequest):
    country = payload.country.upper()
    if country not in ("CA", "US"):
        raise HTTPException(status_code=400, detail="country must be 'CA' or 'US'")

    base_data = {
        "jurisdiction": payload.jurisdiction,
        "seller_name": payload.seller.name,
        "buyer_name": payload.buyer.name,
        "assignor_name": payload.buyer.name,
        "assignee_name": payload.buyer.name,  # you can change this if you track separate assignee
        "address": payload.address,
        "legal_description": payload.legal_description or "",
        "purchase_price": f"{payload.purchase_price:,.2f}",
        "assignment_fee": f"{payload.assignment_fee:,.2f}",
        "deposit_amount": f"{payload.deposit_amount:,.2f}",
        "offer_date": payload.offer_date.isoformat(),
        "closing_date": payload.closing_date.isoformat(),
        "inspection_period_days": payload.inspection_period_days,
        "special_terms": payload.special_terms or "",
    }

    if country == "CA":
        purchase_html = fill_template(CANADA_PURCHASE_TEMPLATE, base_data)
        assignment_html = fill_template(CANADA_ASSIGNMENT_TEMPLATE, base_data)
    else:
        purchase_html = fill_template(USA_PURCHASE_TEMPLATE, base_data)
        assignment_html = fill_template(USA_ASSIGNMENT_TEMPLATE, base_data)

    purchase_pdf_b64 = html_to_pdf_b64(purchase_html)
    assignment_pdf_b64 = html_to_pdf_b64(assignment_html)

    return JSONResponse(
        content=ContractResponse(
            purchase_agreement_pdf_b64=purchase_pdf_b64,
            assignment_contract_pdf_b64=assignment_pdf_b64,
        ).dict()
    )
