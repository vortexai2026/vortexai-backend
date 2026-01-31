from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import tempfile
import os

def generate_pdf(deal: dict) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER

    y = height - 50
    c.setFont("Helvetica", 12)

    c.drawString(50, y, "VortexAI Deal Report")
    y -= 30

    for key, value in deal.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 18
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return path
