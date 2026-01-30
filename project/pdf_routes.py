import os
import psycopg2
import requests
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

from pdf_generator import generate_contract_pdf, pdf_path_for_deal

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "vortexAIinvestors@gmail.com")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")

router = APIRouter(prefix="/contracts", tags=["contracts"])

GREEN_SCORE = float(os.getenv("GREEN_SCORE", "75"))  # you can change anytime

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def send_email(to, subject, html):
    if not BREVO_API_KEY:
        print("[EMAIL MOCK]", to, subject, html[:80])
        return

    requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
        json={
            "sender": {"email": FROM_EMAIL},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": html
        },
        timeout=15
    )

def deal_color(ai_score):
    try:
        s = float(ai_score or 0)
    except:
        s = 0
    if s >= GREEN_SCORE:
        return "green"
    if s >= 55:
        return "yellow"
    return "red"

@router.post("/generate/{deal_id}")
def generate_for_deal(deal_id: str):
    """
    Generates a DRAFT PDF contract for GREEN deals only.
    Emails ADMIN with download link.
    """
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM deals WHERE id = %s", (deal_id,))
        deal = cur.fetchone()
        cur.close()

        if not deal:
            return JSONResponse(404, {"error": "Deal not found"})

        color = deal_color(deal.get("ai_score"))
        if color != "green":
            return JSONResponse(400, {
                "error": "Deal is not GREEN. PDF generation blocked.",
                "deal_color": color,
                "ai_score": str(deal.get("ai_score"))
            })

        # Generate PDF
        path = generate_contract_pdf(deal)

        # Optional: set status in DB (status column exists)
        cur2 = conn.cursor()
        cur2.execute("UPDATE deals SET status = 'contract_ready' WHERE id = %s", (deal_id,))
        conn.commit()
        cur2.close()

        download_url = f"{APP_URL}/contracts/download/{deal_id}"

        # Email you
        send_email(
            ADMIN_EMAIL,
            "🟢 ACTION REQUIRED: Green Deal – Draft Contract Ready",
            f"""
            <h3>Green Deal Contract Draft Ready</h3>
            <p><b>Deal:</b> {deal.get('title','(no title)')}</p>
            <p><b>Location:</b> {deal.get('location','')}</p>
            <p><b>Price:</b> {deal.get('price','')}</p>
            <p><b>AI Score:</b> {deal.get('ai_score','')}</p>
            <p><a href="{download_url}">Download Draft PDF</a></p>
            <p style="color:#888">Draft only. Human review required.</p>
            """
        )

        return {"status": "ok", "deal_id": deal_id, "pdf_path": path, "download_url": download_url}

    except Exception as e:
        conn.rollback()
        return JSONResponse(500, {"error": str(e)})
    finally:
        conn.close()

@router.get("/download/{deal_id}")
def download(deal_id: str):
    path = pdf_path_for_deal(deal_id)
    if not os.path.exists(path):
        return JSONResponse(404, {"error": "PDF not found. Generate first."})
    return FileResponse(path, media_type="application/pdf", filename=os.path.basename(path))
