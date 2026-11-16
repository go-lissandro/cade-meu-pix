from uuid import UUID
from sqlalchemy.orm import Session
from app.models.client import Client
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: Session):
        super().__init__(Client, db)

    def get_by_id_and_user(self, client_id: UUID, user_id: UUID) -> Client | None:
        return (
            self.db.query(Client)
            .filter(Client.id == client_id, Client.user_id == user_id)
            .first()
        )

    def list_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Client], int]:
        query = self.db.query(Client).filter(Client.user_id == user_id)
        if status:
            query = query.filter(Client.status == status)
        total = query.count()
        items = query.order_by(Client.name).offset(skip).limit(limit).all()
        return items, total

    def email_exists_for_user(self, email: str, user_id: UUID, exclude_id: UUID | None = None) -> bool:
        query = self.db.query(Client).filter(
            Client.email == email, Client.user_id == user_id
        )
        if exclude_id:
            query = query.filter(Client.id != exclude_id)
        return query.first() is not None