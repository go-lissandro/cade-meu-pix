from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/charges/{charge_id}/payments", tags=["payments"])


@router.post("/", response_model=PaymentOut, status_code=201)
def register_payment(
    charge_id: UUID,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PaymentService(db).register(charge_id, current_user.id, data)


@router.get("/", response_model=list[PaymentOut])
def list_payments(
    charge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PaymentService(db).list_by_charge(charge_id, current_user.id)