from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone

from app.database import execute, fetch_all


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def take_action(
    deal: Dict[str, Any],
    scores: Dict[str, float],
    decision: Dict[str, Any],
) -> Dict[str, Any]:
    """
    LEVEL 4 – ACTION AI

    Purpose:
    - Based on Level 3 decision, do actions:
      - notify_buyers (save "match" rows)
      - queue_for_review (mark status)
      - discard (mark status)
    - Works without any external services
    - You can later plug in Twilio/Email/etc.
    """

    deal_id = str(deal.get("id") or "").strip()
    if not deal_id:
        return {"ok": False, "error": "deal_id missing on deal object"}

    action = decision.get("action", "queue_for_review")
    priority = decision.get("priority", "medium")

    # Always update deal status
    if action == "notify_buyers":
        status = "matched"
    elif action == "discard":
        status = "discarded"
    else:
        status = "review"

    execute(
        """
        UPDATE deals
        SET status=%s, updated_at=%s,
            profit_score=%s, urgency_score=%s, risk_score=%s, ai_score=%s,
            decision_action=%s, decision_priority=%s
        WHERE id=%s
        """,
        (
            status,
            _utc_now(),
            scores.get("profit_score", 0),
            scores.get("urgency_score", 0),
            scores.get("risk_score", 0),
            scores.get("ai_score", 0),
            action,
            priority,
            deal_id,
        ),
    )

    # If not notify_buyers, we're done
    if action != "notify_buyers":
        return {
            "ok": True,
            "deal_id": deal_id,
            "status": status,
            "action": action,
            "note": "No buyer matching performed (not a notify action).",
        }

    # Get buyers (simple matching rules)
    asset_type = (deal.get("asset_type") or "").lower()
    price = float(deal.get("price") or 0)

    buyers = fetch_all(
        """
        SELECT id, email, name, budget, asset_type, tier
        FROM buyers
        WHERE (asset_type IS NULL OR asset_type=%s OR asset_type='any')
        """,
        (asset_type,),
    )

    matched = []
    for b in buyers:
        budget = float(b.get("budget") or 0)
        # basic rule: if buyer has budget and deal price <= budget
        if budget > 0 and price > 0 and price > budget:
            continue

        match_id = str(uuid.uuid4())
        execute(
            """
            INSERT INTO deal_matches (
                id, deal_id, buyer_id, status, created_at,
                ai_score, priority
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                match_id,
                deal_id,
                str(b["id"]),
                "notified",
                _utc_now(),
                scores.get("ai_score", 0),
                priority,
            ),
        )
        matched.append(
            {"match_id": match_id, "buyer_id": str(b["id"]), "email": b.get("email")}
        )

    return {
        "ok": True,
        "deal_id": deal_id,
        "status": status,
        "action": action,
        "matched_buyers": matched,
        "matched_count": len(matched),
        "note": "Buyers recorded in deal_matches. Plug email/SMS later.",
    }
