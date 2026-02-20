from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal
from app.services.buyer_matcher import match_buyers_for_deal
from app.services.mailer import send_email

def build_deal_email(deal: Deal) -> tuple[str, str]:
    subject = f"🔥 Off-Market Deal: {deal.address} ({deal.market_tag})"
    body = (
        f"Deal: {deal.address}, {deal.city}, {deal.state} {deal.zip_code}\n\n"
        f"Seller Price: ${deal.seller_price:,.0f}\n"
        f"ARV: ${deal.arv_estimated:,.0f}\n"
        f"Repairs: ${deal.repair_estimate:,.0f}\n"
        f"MAO: ${deal.mao:,.0f}\n"
        f"Spread: ${deal.spread:,.0f}\n"
        f"Confidence: {deal.confidence_score}\n"
        f"Flag: {deal.profit_flag}\n\n"
        f"Reply with: INTERESTED + Proof of Funds.\n"
    )
    return subject, body

async def blast_deal_to_buyers(db: AsyncSession, deal: Deal) -> dict:
    buyers = await match_buyers_for_deal(db, deal)
    subject, body = build_deal_email(deal)

    sent = 0
    for b in buyers:
        if b.email:
            send_email(b.email, subject, body)
            sent += 1

    return {"buyers_matched": len(buyers), "emails_sent": sent}
