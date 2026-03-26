import uuid
from datetime import datetime, time
from sqlalchemy import Boolean, ForeignKey, Integer, Time, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class ResendConfig(Base, TimestampMixin):
    __tablename__ = "resend_configs"
    __table_args__ = (
        Index("ix_resend_next_send_active", "next_send_at", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    charge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("charges.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    interval_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    attempts_done: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    send_time: Mapped[time] = mapped_column(Time, nullable=False)
    next_send_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    charge = relationship("Charge", back_populates="resend_config")