import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

PDF_DIR = os.getenv("PDF_DIR", "pdf_out")

def ensure_pdf_dir():
    os.makedirs(PDF_DIR, exist_ok=True)

def pdf_path_for_deal(deal_id: str) -> str:
    ensure_pdf_dir()
    return os.path.join(PDF_DIR, f"contract_{deal_id}.pdf")

def draw_watermark(c: canvas.Canvas, text: str):
    c.saveState()
    c.setFont("Helvetica-Bold", 36)
    c.setFillGray(0.9, 0.5)
    c.translate(80, 250)
    c.rotate(35)
    c.drawString(0, 0, text)
    c.restoreState()

def safe_str(v, default=""):
    if v is None:
        return default
    return str(v)

def generate_contract_pdf(deal: dict) -> str:
    """
    Creates a DRAFT PDF for a given deal dict (from DB).
    Returns the file path.
    """
    deal_id = safe_str(deal.get("id"))
    path = pdf_path_for_deal(deal_id)

    title = safe_str(deal.get("title"), "Deal Contract Draft")
    category = safe_str(deal.get("category"))
    asset_type = safe_str(deal.get("asset_type"))
    location = safe_str(deal.get("location"))
    price = safe_str(deal.get("price"))
    source = safe_str(deal.get("source"))
    ai_score = safe_str(deal.get("ai_score"))
    profit_est = safe_str(deal.get("profit_estimate"))

    estimated_fee = safe_str(deal.get("estimated_fee"))
    fee_type = safe_str(deal.get("fee_type"))
    fee_percent = safe_str(deal.get("fee_percent"))
    actual_fee = safe_str(deal.get("actual_fee"))
    fee_paid = safe_str(deal.get("fee_paid"))

    created_at = safe_str(deal.get("created_at"))
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER

    # Watermark
    draw_watermark(c, "DRAFT - HUMAN REVIEW REQUIRED")

    # Header
    c.setFillGray(0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 60, "VortexAI Contract Draft (NOT SIGNED)")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Generated: {now}")
    c.drawString(50, height - 95, "WARNING: This is a draft prepared by software. Review before signing.")

    # Deal box
    y = height - 130
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Deal Summary")
    y -= 18

    c.setFont("Helvetica", 10)
    lines = [
        f"Title: {title}",
        f"Category: {category} | Asset Type: {asset_type}",
        f"Location: {location}",
        f"Price: {price}",
        f"Source: {source}",
        f"AI Score: {ai_score} | Profit Estimate: {profit_est}",
        f"Deal Created At (DB): {created_at}",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 14

    # Fee section
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Fee Terms (Draft)")
    y -= 18

    c.setFont("Helvetica", 10)
    fee_lines = [
        f"Estimated Fee: {estimated_fee}",
        f"Fee Type: {fee_type} | Fee Percent: {fee_percent}",
        f"Actual Fee (if agreed): {actual_fee}",
        f"Fee Paid (DB flag): {fee_paid}",
        "",
        "NOTE: Success fee is due only upon closing / signed agreement (your policy).",
    ]
    for line in fee_lines:
        c.drawString(50, y, line)
        y -= 14

    # Sign section
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Signatures (Manual)")
    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Your Company / Facilitator: _______________________   Date: __________")
    y -= 20
    c.drawString(50, y, "Buyer: _________________________________            Date: __________")
    y -= 20
    c.drawString(50, y, "Seller: ________________________________            Date: __________")
    y -= 20

    y -= 10
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, y, "This draft does not create a legal relationship until reviewed and signed by the parties.")

    c.showPage()
    c.save()
    return path
