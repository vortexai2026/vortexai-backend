from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import io

def generate_pdf(deal: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)

    width, height = LETTER
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "VortexAI Deal Report")
    y -= 40

    c.setFont("Helvetica", 11)
    for key, value in deal.items():
        c.drawString(40, y, f"{key}: {value}")
        y -= 18
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
    buffer.seek(0)
    return buffer.read()
