from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_session
from app.models.deal import Deal
from app.models.seller_lead import SellerLead
from app.models.document import Document
from app.models.buyer import Buyer
from app.models.buyer_commitment import BuyerCommitment
from app.models.deal_room import DealRoomToken

from app.schemas.deal import DealEvaluateIn, DealEvaluateOut
from app.services.offer_calc import calculate_offer
from app.services.underwriting import confidence_score
from app.services.pdf_contract import generate_purchase_agreement_pdf
from app.services.token import new_token, expires_in
from app.services.brevo_email import brevo_send_email
from app.services.stripe_payments import create_assignment_checkout

router = APIRouter(prefix="/deals", tags=["Deals"])

@router.get("/")
async def list_deals(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Deal).order_by(Deal.id.desc()).limit(200))
    deals = res.scalars().all()
    return [{
        "id": d.id,
        "address": d.property_address,
        "city": d.city,
        "state": d.state,
        "status": d.status,
        "offer": float(d.offer_price) if d.offer_price is not None else None,
        "arv": float(d.arv) if d.arv is not None else None,
        "spread": float(d.estimated_spread) if d.estimated_spread is not None else None,
        "confidence": d.confidence
    } for d in deals]

@router.post("/{deal_id}/evaluate", response_model=DealEvaluateOut)
async def evaluate_deal(deal_id: int, payload: DealEvaluateIn, session: AsyncSession = Depends(get_session)):
    dres = await session.execute(select(Deal).where(Deal.id == deal_id).limit(1))
    deal = dres.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")

    if payload.arv is None:
        raise HTTPException(400, "Provide arv for MVP evaluation (later AI comps can fill this).")

    repairs = float(payload.repairs or 0)
    arv = float(payload.arv)

    calc = calculate_offer(arv=arv, repairs=repairs, investor_discount=float(payload.investor_discount or 0.70))
    mao = float(calc["mao"])
    offer = float(calc["offer"])

    # spread (simple): mao - offer (0 now). real spread is: (buyer price - contract price - fees)
    spread = max(0.0, (mao - offer)) + float(payload.assignment_fee_target or 10000)

    # find seller asking for confidence scoring (if linked)
    seller_asking = None
    if deal.seller_lead_id:
        sres = await session.execute(select(SellerLead).where(SellerLead.id == deal.seller_lead_id).limit(1))
        sl = sres.scalar_one_or_none()
        if sl and sl.asking_price is not None:
            seller_asking = float(sl.asking_price)

    conf = confidence_score(arv=arv, repairs=repairs, seller_asking=seller_asking)

    deal.arv = arv
    deal.repairs = repairs
    deal.mao = mao
    deal.offer_price = offer
    deal.estimated_spread = spread
    deal.confidence = conf
    deal.status = "EVALUATED"

    await session.commit()

    return DealEvaluateOut(
        deal_id=deal.id,
        arv=arv,
        repairs=repairs,
        mao=mao,
        offer_price=offer,
        estimated_spread=spread,
        confidence=conf
    )

@router.post("/{deal_id}/generate_contract")
async def generate_contract(deal_id: int, buyer_name: str = "Vortex AI Acquisition LLC", session: AsyncSession = Depends(get_session)):
    dres = await session.execute(select(Deal).where(Deal.id == deal_id).limit(1))
    deal = dres.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")

    if not deal.seller_lead_id:
        raise HTTPException(400, "Deal not linked to seller lead")

    sres = await session.execute(select(SellerLead).where(SellerLead.id == deal.seller_lead_id).limit(1))
    seller = sres.scalar_one_or_none()
    if not seller:
        raise HTTPException(404, "Seller lead not found")

    if deal.offer_price is None:
        raise HTTPException(400, "Run /evaluate first (offer_price missing)")

    filename, b64pdf = generate_purchase_agreement_pdf(
        seller_name=seller.full_name,
        buyer_name=buyer_name,
        property_address=deal.property_address,
        city=deal.city,
        state=deal.state,
        zip_code=deal.zip,
        purchase_price=float(deal.offer_price),
    )

    doc = Document(deal_id=deal.id, doc_type="PURCHASE_AGREEMENT", filename=filename, content_base64=b64pdf)
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    return {"ok": True, "document_id": doc.id, "filename": filename}

@router.post("/{deal_id}/send_seller_contract")
async def send_seller_contract(deal_id: int, session: AsyncSession = Depends(get_session)):
    dres = await session.execute(select(Deal).where(Deal.id == deal_id).limit(1))
    deal = dres.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")

    if not deal.seller_lead_id:
        raise HTTPException(400, "Deal not linked to seller lead")

    sres = await session.execute(select(SellerLead).where(SellerLead.id == deal.seller_lead_id).limit(1))
    seller = sres.scalar_one_or_none()
    if not seller or not seller.email:
        raise HTTPException(400, "Seller email missing")

    # Find latest purchase agreement doc
    from sqlalchemy import desc
    ddoc = await session.execute(
        select(Document)
        .where(Document.deal_id == deal.id)
        .where(Document.doc_type == "PURCHASE_AGREEMENT")
        .order_by(desc(Document.id))
        .limit(1)
    )
    doc = ddoc.scalar_one_or_none()
    if not doc:
        raise HTTPException(400, "Generate contract first")

    # In MVP we email a link to download later. For now we just send message.
    subject = f"Purchase Agreement - {deal.property_address}"
    html = f"""
    <p>Hi {seller.full_name},</p>
    <p>Attached is the purchase agreement template for:</p>
    <p><b>{deal.property_address}, {deal.city or ''}, {deal.state or ''} {deal.zip or ''}</b></p>
    <p>Offer Price: <b>${float(deal.offer_price):,.2f}</b></p>
    <p>Reply to confirm and we will coordinate signatures.</p>
    <p>- Vortex AI</p>
    """

    await brevo_send_email(to_email=seller.email, subject=subject, html=html)

    deal.status = "OFFER_SENT"
    await session.commit()
    return {"ok": True, "sent_to": seller.email}

@router.post("/{deal_id}/create_deal_room")
async def create_deal_room(deal_id: int, hours: int = 48, session: AsyncSession = Depends(get_session)):
    # create token
    dres = await session.execute(select(Deal).where(Deal.id == deal_id).limit(1))
    deal = dres.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")

    token = new_token()
    t = DealRoomToken(deal_id=deal.id, token=token, expires_at=expires_in(hours))
    session.add(t)
    await session.commit()
    await session.refresh(t)

    return {"ok": True, "token": token, "deal_room_url": f"/deal-room/{token}"}

@router.post("/{deal_id}/blast_buyers")
async def blast_buyers(deal_id: int, session: AsyncSession = Depends(get_session)):
    dres = await session.execute(select(Deal).where(Deal.id == deal_id).limit(1))
    deal = dres.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")

    # Create deal room token (48h)
    token = new_token()
    t = DealRoomToken(deal_id=deal.id, token=token, expires_at=expires_in(48))
    session.add(t)
    await session.commit()

    # Buyers: send to VIP + Active first
    res = await session.execute(
        select(Buyer)
        .where(Buyer.email.is_not(None))
        .order_by(Buyer.score.desc())
        .limit(50)
    )
    buyers = res.scalars().all()

    sent = 0
    for b in buyers:
        subject = f"Off-Market Deal: {deal.city or ''}, {deal.state or ''} - {deal.property_address}"
        html = f"""
        <p>Hi {b.name},</p>
        <p>We have an off-market opportunity:</p>
        <ul>
          <li><b>Address:</b> {deal.property_address}, {deal.city or ''}, {deal.state or ''} {deal.zip or ''}</li>
          <li><b>ARV:</b> {float(deal.arv) if deal.arv else 'TBD'}</li>
          <li><b>Repairs:</b> {float(deal.repairs) if deal.repairs else 'TBD'}</li>
          <li><b>Price (contract):</b> ${float(deal.offer_price) if deal.offer_price else 0:,.2f}</li>
        </ul>
        <p><b>Deal Room:</b> <a href="{t.token}">{t.token}</a></p>
        <p>Reply “INTERESTED” and send Proof of Funds to move forward.</p>
        <p>- Vortex AI</p>
        """
        await brevo_send_email(to_email=b.email, subject=subject, html=html)
        sent += 1

    deal.status = "BLASTED"
    await session.commit()
    return {"ok": True, "buyers_emailed": sent, "deal_room_token": t.token}

@router.post("/{deal_id}/buyer_commit")
async def buyer_commit(
    deal_id: int,
    buyer_id: int = Form(...),
    deposit_amount: float = Form(0),
    proof_of_funds_base64: str | None = Form(None),
    session: AsyncSession = Depends(get_session),
):
    # Buyer commits to deal (POF + deposit)
    dres = await session.execute(select(Deal).where(Deal.id == deal_id).limit(1))
    if not dres.scalar_one_or_none():
        raise HTTPException(404, "Deal not found")

    bres = await session.execute(select(Buyer).where(Buyer.id == buyer_id).limit(1))
    buyer = bres.scalar_one_or_none()
    if not buyer:
        raise HTTPException(404, "Buyer not found")

    commit = BuyerCommitment(
        deal_id=deal_id,
        buyer_id=buyer_id,
        status="PENDING",
        proof_of_funds_base64=proof_of_funds_base64,
        deposit_amount=deposit_amount if deposit_amount > 0 else None,
    )
    session.add(commit)
    await session.commit()
    await session.refresh(commit)

    return {"ok": True, "commitment_id": commit.id, "status": commit.status}

@router.post("/{deal_id}/collect_assignment_fee")
async def collect_assignment_fee(deal_id: int, buyer_id: int, amount_usd: float = 10000, session: AsyncSession = Depends(get_session)):
    # Create Stripe checkout and attach to commitment
    url = create_assignment_checkout(deal_id=deal_id, amount_usd=float(amount_usd))

    # Find commitment or create one
    cres = await session.execute(
        select(BuyerCommitment)
        .where(BuyerCommitment.deal_id == deal_id)
        .where(BuyerCommitment.buyer_id == buyer_id)
        .limit(1)
    )
    c = cres.scalar_one_or_none()
    if not c:
        c = BuyerCommitment(deal_id=deal_id, buyer_id=buyer_id, status="PENDING")
        session.add(c)
        await session.commit()
        await session.refresh(c)

    c.stripe_checkout_url = url
    await session.commit()

    return {"ok": True, "stripe_checkout_url": url}
