import os
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter

DATABASE_URL = os.getenv("DATABASE_URL")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "vortexAIinvestors@gmail.com")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")

router = APIRouter(prefix="/ai/action", tags=["ai-level4"])

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def send_email(to_email: str, subject: str, html: str):
    if not BREVO_API_KEY:
        print("[EMAIL MOCK]", to_email, subject)
        return

    requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
        json={
            "sender": {"email": FROM_EMAIL},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html
        },
        timeout=15
    )

@router.post("/run-once")
def run_actions_once():
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            select * from ai_actions
            where status='queued'
            order by created_at asc
            limit 10
        """)
        actions = cur.fetchall()

        for a in actions:
            deal_id = a["deal_id"]
            action = a["action"]

            if action == "auto_approve":
                # trigger PDF generation
                pdf_url = f"{APP_URL}/pdf/generate/{deal_id}"
                send_email(
                    ADMIN_EMAIL,
                    "✅ Deal auto-approved (PDF ready)",
                    f"<p>Deal approved: {deal_id}</p><p>Generate PDF: {pdf_url}</p>"
                )

            elif action == "review":
                send_email(
                    ADMIN_EMAIL,
                    "🟡 Deal needs review",
                    f"<p>Deal needs review: {deal_id}</p>"
                )

            elif action == "reject":
                # no email needed, but could log
                pass

            cur.execute("update ai_actions set status='done' where id=%s", (a["id"],))

        conn.commit()
        return {"processed": len(actions)}
    finally:
        conn.close()
