from celery.schedules import crontab
from app.workers.celery_app import celery

celery.conf.beat_schedule = {
    # Dispara cobranças com envio programado para o minuto atual
    "dispatch-due-charges": {
        "task": "app.tasks.status_task.dispatch_due_charges",
        "schedule": crontab(minute="*"),
        "options": {"queue": "status"},
    },
    # Marca cobranças vencidas todo dia às 00:05
    "mark-overdue-charges": {
        "task": "app.tasks.status_task.mark_overdue_charges",
        "schedule": crontab(hour=0, minute=5),
        "options": {"queue": "status"},
    },
    # Processa reenvios pendentes a cada 30 minutos
    "process-resends": {
        "task": "app.tasks.resend_task.process_pending_resends",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": "resend"},
    },
}