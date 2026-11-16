from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut
from app.utils.pagination import PaginatedResponse, PaginationParams


class ClientService:
    def __init__(self, db: Session):
        self.repo = ClientRepository(db)
        self.db = db

    def create(self, user_id: UUID, data: ClientCreate) -> Client:
        client = Client(user_id=user_id, status="active", **data.model_dump())
        self.repo.save(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def list(
        self,
        user_id: UUID,
        params: PaginationParams,
        status: str | None = None,
    ) -> PaginatedResponse:
        items, total = self.repo.list_by_user(
            user_id=user_id, status=status, skip=params.skip, limit=params.limit
        )
        return PaginatedResponse(
            items=[ClientOut.model_validate(c) for c in items],
            total=total,
            **params.model_dump(),
        )

    def get_or_404(self, client_id: UUID, user_id: UUID) -> Client:
        client = self.repo.get_by_id_and_user(client_id, user_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return client

    def update(self, client_id: UUID, user_id: UUID, data: ClientUpdate) -> Client:
        client = self.get_or_404(client_id, user_id)
        changes = data.model_dump(exclude_none=True)
        if "phone" in changes:
            # reaproveita a validação/normalização do cadastro
            changes["phone"] = ClientCreate.validate_phone(changes["phone"])
        for field, value in changes.items():
            setattr(client, field, value)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update_status(self, client_id: UUID, user_id: UUID, status: str) -> Client:
        client = self.get_or_404(client_id, user_id)
        client.status = status
        self.db.commit()
        self.db.refresh(client)
        return client
