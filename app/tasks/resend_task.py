from datetime import datetime, timezone
from app.workers.celery_app import celery
from app.core.database import get_db_context


@celery.task(name="app.tasks.resend_task.process_pending_resends")
def process_pending_resends():
    """Processa reenvios agendados que chegaram ao horário."""
    from app.models.resend_config import ResendConfig
    from app.tasks.whatsapp_task import send_whatsapp_message
    from app.tasks.email_task import send_email_message

    now = datetime.now(timezone.utc)
    dispatched = 0

    with get_db_context() as db:
        configs = (
            db.query(ResendConfig)
            .filter(
                ResendConfig.is_active == True,
                ResendConfig.next_send_at <= now,
                ResendConfig.attempts_done < ResendConfig.max_attempts,
            )
            .all()
        )
        for cfg in configs:
            charge = cfg.charge
            if charge.status in ("paid", "canceled", "overdue"):
                cfg.is_active = False
                continue

            next_attempt = cfg.attempts_done + 1

            if charge.client.phone:
                send_whatsapp_message.delay(str(charge.id), attempt=next_attempt)
            if charge.client.email:
                send_email_message.delay(str(charge.id), attempt=next_attempt)

            cfg.attempts_done = next_attempt

            # Agenda o próximo reenvio
            from datetime import timedelta
            if cfg.attempts_done >= cfg.max_attempts:
                cfg.is_active = False
            else:
                from app.utils.date_utils import next_send_datetime
                cfg.next_send_at = next_send_datetime(cfg.interval_hours, cfg.send_time)

            dispatched += 1

    return {"dispatched": dispatched}