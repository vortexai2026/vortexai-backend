from sqlalchemy import BigInteger, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Buyer(Base):
    __tablename__ = "buyers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)

    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str | None] = mapped_column(Text, nullable=True)

    tier: Mapped[str] = mapped_column(Text, nullable=False, default="Weak Buyer")
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
