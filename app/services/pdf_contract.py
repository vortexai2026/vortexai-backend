import base64
from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def generate_purchase_agreement_pdf(
    seller_name: str,
    buyer_name: str,
    property_address: str,
    city: str | None,
    state: str | None,
    zip_code: str | None,
    purchase_price: float,
) -> tuple[str, str]:
    """
    Returns (filename, base64_pdf)
    This is a TEMPLATE PDF for your workflow.
    Have your attorney review your agreement language per state.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    width, height = LETTER

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "PURCHASE AGREEMENT (TEMPLATE)")
    y -= 30

    c.setFont("Helvetica", 11)
    lines = [
        f"Seller: {seller_name}",
        f"Buyer: {buyer_name}",
        "",
        "Property:",
        f"  {property_address}",
        f"  {city or ''}, {state or ''} {zip_code or ''}",
        "",
        f"Purchase Price: ${purchase_price:,.2f}",
        "",
        "Key Terms (Template):",
        "- Buyer to perform inspection / due diligence period (set your days).",
        "- Buyer may assign this agreement (if permitted in your jurisdiction).",
        "- Closing timeline (set your days).",
        "- Earnest money / deposit (set your amount).",
        "",
        "Signatures:",
        "Seller: ___________________________   Date: __________",
        "Buyer:  ___________________________   Date: __________",
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 16
        if y < 80:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)

    c.showPage()
    c.save()

    pdf_bytes = buf.getvalue()
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    filename = "purchase_agreement_template.pdf"
    return filename, b64
