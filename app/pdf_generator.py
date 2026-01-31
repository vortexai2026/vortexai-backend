from fpdf import FPDF
import os
from datetime import datetime


def generate_pdf(deal: dict) -> str:
    """
    Generates a PDF contract for a deal.
    Returns the file path.
    """

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "VortexAI Deal Summary", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", size=12)

    fields = {
        "Title": deal.get("title"),
        "Location": deal.get("location"),
        "Price": deal.get("price"),
        "AI Score": deal.get("ai_score"),
        "Asset Type": deal.get("asset_type"),
        "Category": deal.get("category"),
        "Created At": str(deal.get("created_at")),
    }

    for k, v in fields.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, f"Generated {datetime.utcnow()} UTC", ln=True)

    os.makedirs("/tmp/pdfs", exist_ok=True)
    file_path = f"/tmp/pdfs/deal_{deal['id']}.pdf"
    pdf.output(file_path)

    return file_path
