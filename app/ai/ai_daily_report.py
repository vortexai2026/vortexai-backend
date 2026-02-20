from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.deal import Deal

def _render_html(deals: list[Deal]) -> str:
    by_market: dict[str, list[Deal]] = {}
    for d in deals:
        by_market.setdefault(d.market_tag or "UNKNOWN", []).append(d)

    rows = []
    for market, items in by_market.items():
        rows.append(f"<h2>{market} — {len(items)} GREEN</h2>")
        rows.append("<ul>")
        for d in items:
            rows.append(
                "<li>"
                f"<b>{(d.address or '')}</b>, {(d.city or '')}, {(d.state or '')} {(d.zip_code or '')}"
                f"<br/>Price: ${d.seller_price or 0:,.0f} | ARV: ${d.arv_estimated or 0:,.0f} | "
                f"Repairs: ${d.repair_estimate or 0:,.0f} | Spread: ${d.spread or 0:,.0f} | "
                f"Conf: {d.confidence_score or 0}"
                f"<br/>Deal ID: {d.id}"
                "</li><br/>"
            )
        rows.append("</ul>")

    return (
        "<html><body>"
        "<h1>Vortex AI — Daily GREEN Deals</h1>"
        + "".join(rows)
        + "</body></html>"
    )

def _send_email(subject: str, html: str) -> None:
    if not (settings.REPORT_TO_EMAIL and settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASS and settings.SMTP_FROM):
        # No email config -> do nothing (but keep system stable)
        return

    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = settings.REPORT_TO_EMAIL

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.sendmail(settings.SMTP_FROM, [settings.REPORT_TO_EMAIL], msg.as_string())

async def send_daily_green_report(db: AsyncSession) -> int:
    """
    Pull green deals from last 24h and email them.
    Returns count sent.
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    q = select(Deal).where(
        Deal.profit_flag == "green",
        Deal.created_at >= since,
        Deal.market_tag.in_(settings.MARKETS),
    ).order_by(Deal.market_tag.asc(), Deal.spread.desc().nullslast())

    res = await db.execute(q)
    deals = list(res.scalars().all())

    if not deals:
        return 0

    html = _render_html(deals)
    subject = f"Vortex AI — {len(deals)} GREEN Deals (Dallas/Atlanta) — {now.date().isoformat()}"
    _send_email(subject, html)
    return len(deals)
