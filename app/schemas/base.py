from typing import Generic, TypeVar, Type
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: UUID) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def save(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        self.db.flush()  # popula o id sem commitar (o commit fica na camada de service)
        return instance

    def delete(self, instance: ModelType) -> None:
        self.db.delete(instance)
        self.db.flush()