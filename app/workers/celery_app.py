from celery import Celery
from app.core.config import settings

celery = Celery(
    "cobrancas",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.whatsapp_task",
        "app.tasks.email_task",
        "app.tasks.resend_task",
        "app.tasks.status_task",
    ],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_acks_late=True,          # confirma só após concluir (evita perda de tarefa)
    worker_prefetch_multiplier=1, # um job por vez por worker (melhor distribuição)
    task_routes={
        "app.tasks.whatsapp_task.*": {"queue": "whatsapp"},
        "app.tasks.email_task.*": {"queue": "email"},
        "app.tasks.resend_task.*": {"queue": "resend"},
        "app.tasks.status_task.*": {"queue": "status"},
    },
)