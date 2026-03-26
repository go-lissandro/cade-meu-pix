from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.payment import Payment
from app.repositories.charge_repository import ChargeRepository
from app.schemas.payment import PaymentCreate


class PaymentService:
    def __init__(self, db: Session):
        self.charge_repo = ChargeRepository(db)
        self.db = db

    def register(self, charge_id: UUID, user_id: UUID, data: PaymentCreate) -> Payment:
        charge = self.charge_repo.get_with_relations(charge_id, user_id)
        if not charge:
            raise HTTPException(status_code=404, detail="Cobrança não encontrada")
        if charge.status == "canceled":
            raise HTTPException(status_code=422, detail="Cobrança cancelada")
        if charge.status == "paid":
            raise HTTPException(status_code=422, detail="Cobrança já totalmente paga")

        payment = Payment(charge_id=charge_id, **data.model_dump())
        self.db.add(payment)
        self.db.flush()

        # Recalcula status com o novo pagamento incluído
        total_paid: Decimal = sum(
            p.amount_paid for p in charge.payments
        ) + data.amount_paid

        if total_paid >= charge.amount:
            charge.status = "paid"
            # Para os reenvios automaticamente
            if charge.resend_config:
                charge.resend_config.is_active = False
        elif total_paid > 0:
            charge.status = "partially_paid"

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def list_by_charge(self, charge_id: UUID, user_id: UUID) -> list[Payment]:
        charge = self.charge_repo.get_by_id_and_user(charge_id, user_id)
        if not charge:
            raise HTTPException(status_code=404, detail="Cobrança não encontrada")
        return (
            self.db.query(Payment)
            .filter(Payment.charge_id == charge_id)
            .order_by(Payment.payment_date.desc())
            .all()
        )