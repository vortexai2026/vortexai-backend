from sqlalchemy import BigInteger, Text, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class SellerLead(Base):
    __tablename__ = "seller_leads"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)

    property_address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str | None] = mapped_column(Text, nullable=True)
    zip: Mapped[str | None] = mapped_column(Text, nullable=True)

    asking_price: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
