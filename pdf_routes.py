from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import uuid
import os

def generate_pdf(deal: dict) -> str:
    filename = f"/tmp/contract_{uuid.uuid4()}.pdf"
    c = canvas.Canvas(filename, pagesize=LETTER)

    c.setFont("Helvetica", 12)
    c.drawString(50, 750, "VortexAI Deal Contract")
    c.drawString(50, 720, f"Title: {deal.get('title','')}")
    c.drawString(50, 700, f"Location: {deal.get('location','')}")
    c.drawString(50, 680, f"Price: {deal.get('price','')}")
    c.drawString(50, 660, f"AI Score: {deal.get('ai_score','')}")

    c.drawString(50, 620, "This contract is auto-generated for review.")
    c.drawString(50, 600, "Final approval required before signing.")

    c.showPage()
    c.save()

    return filename
