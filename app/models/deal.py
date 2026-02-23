from sqlalchemy import BigInteger, Text, Numeric, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    seller_lead_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    property_address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str | None] = mapped_column(Text, nullable=True)
    zip: Mapped[str | None] = mapped_column(Text, nullable=True)

    arv: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    repairs: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    mao: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    offer_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    estimated_spread: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(Text, nullable=False, default="NEW")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
