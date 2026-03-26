from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, clients, charges, payments, dashboard

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(clients.router)
api_router.include_router(charges.router)
api_router.include_router(payments.router)
api_router.include_router(dashboard.router)