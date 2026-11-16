import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, field_validator
from app.schemas.payment import PaymentOut


ChargeStatus = Literal["pending", "partially_paid", "paid", "canceled", "overdue"]


class ResendConfigSchema(BaseModel):
    interval_hours: int = 24
    max_attempts: int = 3
    send_time: str  # "HH:MM"


class ChargeCreate(BaseModel):
    client_id: uuid.UUID
    amount: Decimal
    description: str
    due_date: date
    send_at: datetime
    resend_config: ResendConfigSchema | None = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Data de vencimento não pode ser no passado")
        return v


class ChargeUpdate(BaseModel):
    amount: Decimal | None = None
    description: str | None = None
    due_date: date | None = None
    send_at: datetime | None = None


class ChargeOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    client_id: uuid.UUID
    amount: Decimal
    description: str
    due_date: date
    send_at: datetime
    status: ChargeStatus
    created_at: datetime
    updated_at: datetime


class ChargeDetailOut(ChargeOut):
    payments: list[PaymentOut] = []