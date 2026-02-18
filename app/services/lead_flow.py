import csv
import io
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal


@dataclass
class NormalizedLead:
    address: str
    city: str
    state: str
    zip: str
    asking_price: Optional[float]
    beds: Optional[int]
    baths: Optional[float]
    sqft: Optional[int]
    source: str
    raw_text: str


def _clean(x: Any) -> str:
    return str(x or "").strip()


def _to_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def _to_int(x: Any) -> Optional[int]:
    try:
        return int(float(x))
    except Exception:
        return None


def _lead_hash(n: NormalizedLead) -> str:
    key = f"{n.address}|{n.city}|{n.state}|{n.zip}|{n.asking_price}"
    return hashlib.sha256(key.lower().encode("utf-8")).hexdigest()


def normalize(payload: Dict[str, Any], source: str) -> NormalizedLead:
    return NormalizedLead(
        address=_clean(payload.get("address") or payload.get("street")),
        city=_clean(payload.get("city")),
        state=_clean(payload.get("state")).upper(),
        zip=_clean(payload.get("zip") or payload.get("zipcode")),
        asking_price=_to_float(payload.get("asking_price") or payload.get("price") or payload.get("list_price")),
        beds=_to_int(payload.get("beds") or payload.get("bedrooms")),
        baths=_to_float(payload.get("baths") or payload.get("bathrooms")),
        sqft=_to_int(payload.get("sqft") or payload.get("square_feet")),
        source=source,
        raw_text=_clean(payload.get("description") or payload.get("raw") or ""),
    )


async def upsert_deal(db: AsyncSession, lead: NormalizedLead) -> Deal:
    if not lead.address or not lead.state:
        raise ValueError("Lead must contain at least address + state")

    ext_id = _lead_hash(lead)

    # Adjust column names to match your Deal model
    existing = (await db.execute(select(Deal).where(Deal.external_id == ext_id))).scalars().first()
    if existing:
        return existing

    deal = Deal(
        external_id=ext_id,
        address=lead.address,
        city=lead.city,
        state=lead.state,
        zip=lead.zip,
        asking_price=lead.asking_price,
        beds=lead.beds,
        baths=lead.baths,
        sqft=lead.sqft,
        source=lead.source,
        notes=lead.raw_text,
        status="NEW",
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


async def ingest_webhook(db: AsyncSession, payload: Dict[str, Any], source: str = "WEBHOOK") -> Deal:
    return await upsert_deal(db, normalize(payload, source))


async def ingest_csv_bytes(db: AsyncSession, csv_bytes: bytes, source: str = "CSV_UPLOAD") -> List[Deal]:
    text = csv_bytes.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    out: List[Deal] = []
    for row in reader:
        try:
            out.append(await upsert_deal(db, normalize(row, source)))
        except Exception:
            continue
    return out
