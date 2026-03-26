from datetime import datetime, date, timezone
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.charge import Charge
from app.repositories.base import BaseRepository


class ChargeRepository(BaseRepository[Charge]):
    def __init__(self, db: Session):
        super().__init__(Charge, db)

    def get_by_id_and_user(self, charge_id: UUID, user_id: UUID) -> Charge | None:
        return (
            self.db.query(Charge)
            .filter(Charge.id == charge_id, Charge.user_id == user_id)
            .first()
        )

    def get_with_relations(self, charge_id: UUID, user_id: UUID) -> Charge | None:
        return (
            self.db.query(Charge)
            .options(
                joinedload(Charge.client),
                joinedload(Charge.payments),
                joinedload(Charge.resend_config),
            )
            .filter(Charge.id == charge_id, Charge.user_id == user_id)
            .first()
        )

    def list_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
        client_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Charge], int]:
        query = (
            self.db.query(Charge)
            .filter(Charge.user_id == user_id)
            .options(joinedload(Charge.client))
        )
        if status:
            query = query.filter(Charge.status == status)
        if client_id:
            query = query.filter(Charge.client_id == client_id)
        if date_from:
            query = query.filter(Charge.due_date >= date_from)
        if date_to:
            query = query.filter(Charge.due_date <= date_to)

        total = query.count()
        items = query.order_by(Charge.due_date.asc()).offset(skip).limit(limit).all()
        return items, total

    def get_due_for_sending(self, now: datetime) -> list[Charge]:
        """Cobranças agendadas para envio até agora, ainda pendentes."""
        return (
            self.db.query(Charge)
            .options(joinedload(Charge.client), joinedload(Charge.resend_config))
            .filter(
                Charge.send_at <= now,
                Charge.status.in_(["pending", "partially_paid"]),
            )
            .all()
        )

    def get_overdue_pending(self, today: date) -> list[Charge]:
        """Cobranças vencidas que ainda estão como pending."""
        return (
            self.db.query(Charge)
            .filter(
                Charge.due_date < today,
                Charge.status.in_(["pending", "partially_paid"]),
            )
            .all()
        )

    def get_for_calendar(self, user_id: UUID, year: int, month: int) -> list[Charge]:
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        start = date(year, month, 1)
        end = date(year, month, last_day)
        return (
            self.db.query(Charge)
            .options(joinedload(Charge.client))
            .filter(
                Charge.user_id == user_id,
                Charge.due_date >= start,
                Charge.due_date <= end,
            )
            .order_by(Charge.due_date)
            .all()
        )