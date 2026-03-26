import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, field_validator

PaymentMethod = Literal["pix", "transfer", "cash", "card", "boleto"]


class PaymentCreate(BaseModel):
    amount_paid: Decimal
    payment_date: date
    method: PaymentMethod
    notes: str | None = None

    @field_validator("amount_paid")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v


class PaymentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    charge_id: uuid.UUID
    amount_paid: Decimal
    payment_date: date
    method: str
    notes: str | None
    created_at: datetime