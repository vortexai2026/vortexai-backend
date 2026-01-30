import os
import time
import psycopg2
import requests
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
APP_URL = os.getenv("APP_URL", "http://localhost:8080")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "vortexAIinvestors@gmail.com")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@vortexai.local")

REMINDER_EVERY_SECONDS = int(os.getenv("REMINDER_EVERY_SECONDS", "10800"))  # 3 hours default

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def send_email(to, subject, html):
    if not BREVO_API_KEY:
        print("[EMAIL MOCK]", to, subject)
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

def run_once():
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # remind for deals that are ready but not paid/closed
        cur.execute("""
            SELECT id, title, location, price, ai_score, status, paid
            FROM deals
            WHERE status = 'contract_ready'
              AND (paid IS NULL OR paid = false)
            ORDER BY created_at DESC
            LIMIT 20
        """)
        rows = cur.fetchall()
        cur.close()

        for d in rows:
            deal_id = d["id"]
            download_url = f"{APP_URL}/contracts/download/{deal_id}"
            send_email(
                ADMIN_EMAIL,
                "⏰ REMINDER: Contract Draft Waiting",
                f"""
                <p><b>Deal:</b> {d.get('title','')}</p>
                <p><b>Location:</b> {d.get('location','')}</p>
                <p><b>Price:</b> {d.get('price','')}</p>
                <p><b>AI Score:</b> {d.get('ai_score','')}</p>
                <p><a href="{download_url}">Download Draft PDF</a></p>
                <p style="color:#888">Reminder from VortexAI.</p>
                """
            )

    finally:
        conn.close()

def loop():
    while True:
        run_once()
        time.sleep(REMINDER_EVERY_SECONDS)

if __name__ == "__main__":
    loop()
