from sqlalchemy import BigInteger, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    deal_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    doc_type: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    content_base64: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
