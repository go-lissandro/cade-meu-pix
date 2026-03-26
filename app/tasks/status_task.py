from datetime import datetime, date, timezone
from app.workers.celery_app import celery
from app.core.database import get_db_context


@celery.task(name="app.tasks.status_task.dispatch_due_charges")
def dispatch_due_charges():
    """Verifica cobranças com send_at <= agora e despacha para as filas de envio."""
    from app.tasks.whatsapp_task import send_whatsapp_message
    from app.tasks.email_task import send_email_message
    from app.repositories.charge_repository import ChargeRepository

    now = datetime.now(timezone.utc)
    with get_db_context() as db:
        repo = ChargeRepository(db)
        charges = repo.get_due_for_sending(now)
        dispatched = 0
        for charge in charges:
            client = charge.client
            # Só despacha se ainda não há log de envio bem-sucedido (idempotência)
            already_sent = any(
                log.status == "sent" and log.attempt_number == 1
                for log in charge.message_logs
            )
            if already_sent:
                continue

            if client.phone:
                send_whatsapp_message.delay(str(charge.id), attempt=1)
            if client.email:
                send_email_message.delay(str(charge.id), attempt=1)
            dispatched += 1

    return {"dispatched": dispatched, "at": now.isoformat()}


@celery.task(name="app.tasks.status_task.mark_overdue_charges")
def mark_overdue_charges():
    """Marca cobranças vencidas que ainda estão como pending."""
    from app.repositories.charge_repository import ChargeRepository

    today = date.today()
    with get_db_context() as db:
        repo = ChargeRepository(db)
        charges = repo.get_overdue_pending(today)
        for charge in charges:
            charge.status = "overdue"
            if charge.resend_config:
                charge.resend_config.is_active = False

    return {"marked_overdue": len(charges)}