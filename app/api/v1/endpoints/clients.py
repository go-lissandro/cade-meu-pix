from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate, ClientStatusUpdate, ClientOut
from app.services.client_service import ClientService
from app.utils.pagination import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientOut, status_code=201)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ClientService(db).create(current_user.id, data)


@router.get("/", response_model=PaginatedResponse)
def list_clients(
    status: str | None = Query(None, pattern="^(active|inactive)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    params = PaginationParams(page=page, limit=limit)
    return ClientService(db).list(current_user.id, params, status=status)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ClientService(db).get_or_404(client_id, current_user.id)


@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: UUID,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ClientService(db).update(client_id, current_user.id, data)


@router.patch("/{client_id}/status", response_model=ClientOut)
def update_status(
    client_id: UUID,
    data: ClientStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ClientService(db).update_status(client_id, current_user.id, data.status)