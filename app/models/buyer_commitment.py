from sqlalchemy import BigInteger, Text, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class BuyerCommitment(Base):
    __tablename__ = "buyer_commitments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    deal_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    buyer_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    status: Mapped[str] = mapped_column(Text, nullable=False, default="PENDING")
    proof_of_funds_base64: Mapped[str | None] = mapped_column(Text, nullable=True)
    deposit_amount: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    stripe_checkout_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
