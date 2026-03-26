import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, field_validator
import re


class ClientCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = None
    notes: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) < 10 or len(digits) > 13:
            raise ValueError("Telefone inválido")
        return digits


class ClientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    notes: str | None = None


class ClientStatusUpdate(BaseModel):
    status: Literal["active", "inactive"]


class ClientOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    phone: str
    email: str | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime