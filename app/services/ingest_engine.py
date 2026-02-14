async def ingest_one(db: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    title = str(payload.get("title", "")).strip()
    asset_type = str(payload.get("asset_type", "")).strip()
    city = str(payload.get("city", "")).strip()
    price = float(payload.get("price") or 0)

    external_id = payload.get("external_id")

    if not title or not asset_type or not city or price <= 0 or not external_id:
        return {
            "ok": False,
            "error": "Missing required fields: external_id, title, asset_type, city, price",
        }

    # Normalize lightly
    title_n = " ".join(title.split())
    asset_type_n = " ".join(asset_type.split())
    city_n = " ".join(city.split())

    # 🔎 Check duplicate by external_id (NEW STRONG METHOD)
    existing = await db.scalar(
        select(Deal).where(Deal.external_id == external_id)
    )

    if existing:
        return {
            "ok": True,
            "created": False,
            "deal_id": existing.id,
            "status": getattr(existing, "status", None),
        }

    deal = Deal(
        external_id=external_id,  # 👈 FIXED
        title=title_n,
        asset_type=asset_type_n,
        city=city_n,
        price=price,
        score=float(payload.get("score") or 0.0),
    )

    if hasattr(deal, "arv"):
        deal.arv = payload.get("arv")
    if hasattr(deal, "repairs"):
        deal.repairs = payload.get("repairs")
    if hasattr(deal, "assignment_fee"):
        deal.assignment_fee = payload.get("assignment_fee")

    deal.status = "new"

    db.add(deal)
    await db.flush()

    return {
        "ok": True,
        "created": True,
        "deal_id": deal.id,
        "status": deal.status,
    }
