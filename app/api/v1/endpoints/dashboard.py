from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.charge import Charge
from app.models.payment import Payment
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    counts = dict(
        db.query(Charge.status, func.count(Charge.id))
        .filter(Charge.user_id == current_user.id)
        .group_by(Charge.status)
        .all()
    )

    open_statuses = ("pending", "partially_paid", "overdue")
    total_open = (
        db.query(func.coalesce(func.sum(Charge.amount), 0))
        .filter(Charge.user_id == current_user.id, Charge.status.in_(open_statuses))
        .scalar()
    )
    paid_on_open = (
        db.query(func.coalesce(func.sum(Payment.amount_paid), 0))
        .join(Charge, Payment.charge_id == Charge.id)
        .filter(Charge.user_id == current_user.id, Charge.status.in_(open_statuses))
        .scalar()
    )
    received = (
        db.query(func.coalesce(func.sum(Payment.amount_paid), 0))
        .join(Charge, Payment.charge_id == Charge.id)
        .filter(Charge.user_id == current_user.id, Charge.status != "canceled")
        .scalar()
    )
    charges_today = (
        db.query(func.count(Charge.id))
        .filter(Charge.user_id == current_user.id, Charge.due_date == date.today())
        .scalar()
    )

    return DashboardSummary(
        total_pending=counts.get("pending", 0),
        total_paid=counts.get("paid", 0),
        total_overdue=counts.get("overdue", 0),
        total_partially_paid=counts.get("partially_paid", 0),
        amount_to_receive=Decimal(total_open) - Decimal(paid_on_open),
        amount_received=Decimal(received),
        charges_today=charges_today or 0,
    )
