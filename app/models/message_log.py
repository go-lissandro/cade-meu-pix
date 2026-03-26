import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class MessageLog(Base):
    __tablename__ = "message_logs"
    __table_args__ = (
        Index("ix_message_logs_charge_attempt", "charge_id", "attempt_number"),
        Index("ix_message_logs_user", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    charge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("charges.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)   # whatsapp | email
    status: Mapped[str] = mapped_column(String(20), nullable=False)    # sent | failed
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    charge = relationship("Charge", back_populates="message_logs")