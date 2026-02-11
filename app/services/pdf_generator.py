from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from typing import Dict, Any

def generate_pdf(deal: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "VortexAI Deal Report")

    c.setFont("Helvetica", 12)
    y = height - 100
    for k in ["id", "title", "price", "location", "asset_type", "source", "ai_score", "decision", "next_action"]:
        c.drawString(50, y, f"{k}: {deal.get(k, '')}")
        y -= 20

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()
