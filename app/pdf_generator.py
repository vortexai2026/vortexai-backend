from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from typing import Dict, Any

def generate_pdf(deal: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 60, "VortexAI Deal Report")

    c.setFont("Helvetica", 11)
    y = h - 100

    fields = [
        ("Deal ID", str(deal.get("id"))),
        ("Title", str(deal.get("title"))),
        ("Price", str(deal.get("price"))),
        ("Location", str(deal.get("location"))),
        ("Asset Type", str(deal.get("asset_type"))),
        ("Source", str(deal.get("source"))),
        ("Status", str(deal.get("status"))),
        ("AI Score", str(deal.get("ai_score"))),
        ("Profit Score", str(deal.get("profit_score"))),
        ("Urgency Score", str(deal.get("urgency_score"))),
        ("Risk Score", str(deal.get("risk_score"))),
    ]

    for k, v in fields:
        c.drawString(50, y, f"{k}: {v}")
        y -= 18

    c.showPage()
    c.save()

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
