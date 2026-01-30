import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime

PDF_DIR = "pdf_out"

def ensure_dir():
    os.makedirs(PDF_DIR, exist_ok=True)

def generate_pdf(deal: dict) -> str:
    ensure_dir()

    deal_id = deal.get("id")
    filename = f"{PDF_DIR}/deal_{deal_id}.pdf"

    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    # Watermark
    c.setFont("Helvetica-Bold", 36)
    c.setFillGray(0.9, 0.4)
    c.rotate(30)
    c.drawString(150, 100, "DRAFT – HUMAN REVIEW REQUIRED")
    c.rotate(-30)
    c.setFillGray(0)

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "VortexAI Deal Contract (DRAFT)")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Generated: {datetime.utcnow()} UTC")

    y = height - 120
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Deal Details")
    y -= 20

    c.setFont("Helvetica", 10)
    fields = [
        ("Title", deal.get("title")),
        ("Category", deal.get("category")),
        ("Asset Type", deal.get("asset_type")),
        ("Location", deal.get("location")),
        ("Price", deal.get("price")),
        ("AI Score", deal.get("ai_score")),
        ("Estimated Fee", deal.get("estimated_fee")),
        ("Status", deal.get("status")),
    ]

    for label, value in fields:
        c.drawString(50, y, f"{label}: {value}")
        y -= 15

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Signatures (Manual)")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Your Company: ______________________   Date: ________")
    y -= 20
    c.drawString(50, y, "Buyer: _____________________________   Date: ________")
    y -= 20
    c.drawString(50, y, "Seller: ____________________________   Date: ________")

    c.showPage()
    c.save()

    return filename

