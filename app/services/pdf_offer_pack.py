# app/services/pdf_offer_pack.py

import os
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def generate_offer_pdf_bytes(
    deal_title: str,
    deal_city: str,
    offer_price: float,
    terms_text: str
) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    y = height - 72
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "OFFER TO PURCHASE (AS-IS)")
    y -= 28

    c.setFont("Helvetica", 11)
    c.drawString(72, y, f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
    y -= 18

    c.drawString(72, y, f"Property: {deal_title}")
    y -= 18

    c.drawString(72, y, f"Market: {deal_city}")
    y -= 18

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, f"Offer Price: ${int(offer_price):,} (cash)")
    y -= 24

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, "Terms:")
    y -= 18

    c.setFont("Helvetica", 11)
    for line in terms_text.splitlines():
        if not line.strip():
            y -= 10
            continue
        # page break safety
        if y < 72:
            c.showPage()
            y = height - 72
            c.setFont("Helvetica", 11)
        c.drawString(82, y, line.strip())
        y -= 14

    y -= 18
    c.drawString(72, y, "If accepted, reply “YES” and we will send the purchase agreement immediately.")
    y -= 40

    c.drawString(72, y, "Signed,")
    y -= 18
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, y, "Vortex AI Deals")

    c.showPage()
    c.save()
    return buffer.getvalue()


def save_offer_pdf(deal_id: int, pdf_bytes: bytes) -> str:
    """
    Saves to local disk inside container.
    For production, you can later upload to S3/Supabase Storage.
    """
    out_dir = os.getenv("PDF_OUTPUT_DIR", "/app/generated_pdfs")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, f"offer_deal_{deal_id}.pdf")
    with open(path, "wb") as f:
        f.write(pdf_bytes)

    return path
