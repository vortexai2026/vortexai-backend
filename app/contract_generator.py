import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

TEMPLATE_PATH = Path("app/templates/assignment_contract.txt")

def render_contract_text(data: Dict[str, Any]) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    filled = template.format(
        date=data.get("date") or datetime.utcnow().strftime("%Y-%m-%d"),
        seller_name=data.get("seller_name","UNKNOWN"),
        buyer_name=data.get("buyer_name","UNKNOWN"),
        asset_title=data.get("asset_title",""),
        location=data.get("location",""),
        price=data.get("price",""),
        currency=data.get("currency","USD"),
        closing_days=data.get("closing_days", 14),
    )
    return filled

def generate_contract_pdf(data: Dict[str, Any]) -> str:
    text = render_contract_text(data)
    file_id = str(uuid.uuid4())
    out_path = f"/tmp/contract_{file_id}.pdf"

    c = canvas.Canvas(out_path, pagesize=letter)
    width, height = letter

    y = height - 50
    for line in text.splitlines():
        c.drawString(40, y, line[:120])
        y -= 14
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return out_path
