# app/outreach_routes.py
import os
from fastapi import APIRouter, HTTPException
from app.database import fetch_all, fetch_one, execute
from app.emailer import send_email

router = APIRouter(prefix="/outreach", tags=["outreach"])

DEFAULT_APPROVER = os.getenv("APPROVER_NAME", "owner")


@router.get("/pending")
def list_pending(limit: int = 50):
    rows = fetch_all(
        """
        SELECT om.*, d.title, d.asset_type, d.location, d.url
        FROM outreach_messages om
        LEFT JOIN deals d ON d.id = om.deal_id
        WHERE om.status IN ('draft','approved')
        ORDER BY om.created_at DESC
        LIMIT %s
        """,
        (limit,),
    )
    return {"count": len(rows), "items": rows}


@router.post("/approve/{message_id}")
def approve_message(message_id: str, approved_by: str = DEFAULT_APPROVER):
    msg = fetch_one("SELECT * FROM outreach_messages WHERE id=%s", (message_id,))
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    execute(
        """
        UPDATE outreach_messages
        SET status='approved', approved_by=%s, approved_at=NOW()
        WHERE id=%s
        """,
        (approved_by, message_id),
    )
    return {"ok": True, "id": message_id, "status": "approved"}


@router.post("/send/{message_id}")
def send_message(message_id: str):
    msg = fetch_one("SELECT * FROM outreach_messages WHERE id=%s", (message_id,))
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    if msg["status"] not in ("approved", "draft"):
        raise HTTPException(status_code=400, detail=f"Cannot send status={msg['status']}")

    channel = (msg.get("channel") or "manual").lower()
    target = (msg.get("target") or "").strip()
    subject = msg.get("subject") or "VortexAI Outreach"
    body = msg.get("body") or ""

    try:
        if channel == "email":
            if not target:
                raise RuntimeError("No email target set")
            send_email(target, subject, body)
            execute(
                """
                UPDATE outreach_messages
                SET status='sent', sent_at=NOW(), error=NULL
                WHERE id=%s
                """,
                (message_id,),
            )
            return {"ok": True, "sent": True, "channel": "email"}

        # manual mode = copy/paste
        execute(
            """
            UPDATE outreach_messages
            SET status='approved', error=NULL
            WHERE id=%s
            """,
            (message_id,),
        )
        return {
            "ok": True,
            "sent": False,
            "channel": "manual",
            "instructions": "Copy body and paste into Facebook/Kijiji chat manually.",
            "body": body,
        }

    except Exception as e:
        execute(
            """
            UPDATE outreach_messages
            SET status='failed', error=%s
            WHERE id=%s
            """,
            (str(e), message_id),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skip/{message_id}")
def skip_message(message_id: str):
    execute("UPDATE outreach_messages SET status='skipped' WHERE id=%s", (message_id,))
    return {"ok": True, "id": message_id, "status": "skipped"}


@router.get("/{message_id}")
def get_message(message_id: str):
    msg = fetch_one("SELECT * FROM outreach_messages WHERE id=%s", (message_id,))
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg
