from app.workers.celery_app import celery
from app.core.database import get_db_context
from app.models.message_log import MessageLog


@celery.task(
    name="app.tasks.whatsapp_task.send_whatsapp_message",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="whatsapp",
)
def send_whatsapp_message(self, charge_id: str, attempt: int = 1):
    from app.integrations.whatsapp import WhatsAppClient
    from app.utils.message_builder import build_whatsapp_message
    with get_db_context() as db:
        # Busca direto pela primary key (sem filtro user_id — task interna)
        from app.models.charge import Charge
        from uuid import UUID
        charge = (
            db.query(Charge)
            .filter(Charge.id == UUID(charge_id))
            .first()
        )
        if not charge:
            return {"skipped": "charge not found"}

        # Interrompe se já foi paga/cancelada
        if charge.status in ("paid", "canceled"):
            return {"skipped": charge.status}

        message = build_whatsapp_message(charge)
        log = MessageLog(
            charge_id=charge.id,
            user_id=charge.user_id,
            channel="whatsapp",
            attempt_number=attempt,
        )

        try:
            client = WhatsAppClient()
            client.send_text(charge.client.phone, message)
            log.status = "sent"
        except Exception as exc:
            log.status = "failed"
            log.error_detail = str(exc)
            db.add(log)
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

        db.add(log)
    return {"sent": charge_id, "attempt": attempt}