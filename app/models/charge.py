import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Text, ForeignKey, Numeric, Date, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Charge(Base, TimestampMixin):
    __tablename__ = "charges"
    __table_args__ = (
        Index("ix_charges_user_status", "user_id", "status"),
        Index("ix_charges_send_at_status", "send_at", "status"),
        Index("ix_charges_due_date", "due_date"),
        Index("ix_charges_client", "client_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    send_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    user = relationship("User", back_populates="charges")
    client = relationship("Client", back_populates="charges")
    payments = relationship("Payment", back_populates="charge", cascade="all, delete-orphan")
    message_logs = relationship("MessageLog", back_populates="charge", cascade="all, delete-orphan")
    resend_config = relationship("ResendConfig", back_populates="charge", uselist=False, cascade="all, delete-orphan")