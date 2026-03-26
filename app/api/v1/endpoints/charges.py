from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.charge import ChargeCreate, ChargeUpdate, ChargeOut, ChargeDetailOut
from app.services.charge_service import ChargeService
from app.utils.pagination import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/charges", tags=["charges"])


@router.post("/", response_model=ChargeOut, status_code=201)
def create_charge(
    data: ChargeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChargeService(db).create(current_user.id, data)


@router.get("/", response_model=PaginatedResponse)
def list_charges(
    status: str | None = Query(None),
    client_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    params = PaginationParams(page=page, limit=limit)
    return ChargeService(db).list(
        current_user.id, params, status=status, client_id=client_id
    )


@router.get("/calendar")
def get_calendar(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.repositories.charge_repository import ChargeRepository
    from app.schemas.charge import ChargeOut
    charges = ChargeRepository(db).get_for_calendar(current_user.id, year, month)
    # Agrupa por dia para o calendário
    result: dict = {}
    for c in charges:
        key = c.due_date.isoformat()
        result.setdefault(key, []).append(ChargeOut.model_validate(c))
    return result


@router.get("/{charge_id}", response_model=ChargeDetailOut)
def get_charge(
    charge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChargeService(db).get_or_404(charge_id, current_user.id)


@router.put("/{charge_id}", response_model=ChargeOut)
def update_charge(
    charge_id: UUID,
    data: ChargeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChargeService(db).update(charge_id, current_user.id, data)


@router.patch("/{charge_id}/cancel", response_model=ChargeOut)
def cancel_charge(
    charge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChargeService(db).cancel(charge_id, current_user.id)


@router.get("/{charge_id}/logs")
def get_message_logs(
    charge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.message_log import MessageLog
    # Garante que a cobrança pertence ao usuário
    ChargeService(db).get_or_404(charge_id, current_user.id)
    return (
        db.query(MessageLog)
        .filter(MessageLog.charge_id == charge_id)
        .order_by(MessageLog.sent_at.desc())
        .all()
    )