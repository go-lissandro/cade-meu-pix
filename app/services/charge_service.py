from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.charge import Charge
from app.models.resend_config import ResendConfig
from app.repositories.charge_repository import ChargeRepository
from app.repositories.client_repository import ClientRepository
from app.schemas.charge import ChargeCreate, ChargeUpdate, ChargeOut
from app.utils.pagination import PaginatedResponse, PaginationParams


class ChargeService:
    def __init__(self, db: Session):
        self.repo = ChargeRepository(db)
        self.client_repo = ClientRepository(db)
        self.db = db

    def create(self, user_id: UUID, data: ChargeCreate) -> Charge:
        # Valida que o cliente pertence ao usuário
        client = self.client_repo.get_by_id_and_user(data.client_id, user_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        if client.status == "inactive":
            raise HTTPException(status_code=422, detail="Cliente inativo")

        charge = Charge(
            user_id=user_id,
            client_id=data.client_id,
            amount=data.amount,
            description=data.description,
            due_date=data.due_date,
            send_at=data.send_at,
            status="pending",
        )
        self.db.add(charge)
        self.db.flush()  # gera o id antes de criar o resend_config

        if data.resend_config:
            from datetime import time
            h, m = map(int, data.resend_config.send_time.split(":"))
            resend = ResendConfig(
                charge_id=charge.id,
                interval_hours=data.resend_config.interval_hours,
                max_attempts=data.resend_config.max_attempts,
                send_time=time(h, m),
            )
            self.db.add(resend)

        self.db.commit()
        self.db.refresh(charge)
        return charge

    def list(
        self,
        user_id: UUID,
        params: PaginationParams,
        status: str | None = None,
        client_id: UUID | None = None,
    ) -> PaginatedResponse:
        items, total = self.repo.list_by_user(
            user_id=user_id,
            status=status,
            client_id=client_id,
            skip=params.skip,
            limit=params.limit,
        )
        return PaginatedResponse(
            items=[ChargeOut.model_validate(c) for c in items],
            total=total,
            **params.model_dump(),
        )

    def get_or_404(self, charge_id: UUID, user_id: UUID) -> Charge:
        charge = self.repo.get_with_relations(charge_id, user_id)
        if not charge:
            raise HTTPException(status_code=404, detail="Cobrança não encontrada")
        return charge

    def update(self, charge_id: UUID, user_id: UUID, data: ChargeUpdate) -> Charge:
        charge = self.get_or_404(charge_id, user_id)
        if charge.status in ("paid", "canceled"):
            raise HTTPException(
                status_code=422,
                detail=f"Não é possível editar cobrança com status '{charge.status}'",
            )
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(charge, field, value)
        self.db.commit()
        self.db.refresh(charge)
        return charge

    def cancel(self, charge_id: UUID, user_id: UUID) -> Charge:
        charge = self.get_or_404(charge_id, user_id)
        if charge.status == "paid":
            raise HTTPException(status_code=422, detail="Cobrança já paga não pode ser cancelada")
        charge.status = "canceled"
        if charge.resend_config:
            charge.resend_config.is_active = False
        self.db.commit()
        return charge