from uuid import UUID
from app.workers.celery_app import celery
from app.core.database import get_db_context
from app.models.message_log import MessageLog


@celery.task(
    name="app.tasks.email_task.send_email_message",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="email",
)
def send_email_message(self, charge_id: str, attempt: int = 1):
    from app.integrations.email_provider import EmailProvider
    from app.models.charge import Charge
    from app.utils.message_builder import build_email_html

    with get_db_context() as db:
        charge = db.query(Charge).filter(Charge.id == UUID(charge_id)).first()
        if not charge:
            return {"skipped": "charge not found"}
        if charge.status in ("paid", "canceled"):
            return {"skipped": charge.status}
        if not charge.client.email:
            return {"skipped": "client without email"}

        log = MessageLog(
            charge_id=charge.id,
            user_id=charge.user_id,
            channel="email",
            attempt_number=attempt,
        )
        try:
            EmailProvider().send(
                to=charge.client.email,
                subject=f"Lembrete de cobrança: {charge.description}",
                body_html=build_email_html(charge),
            )
            log.status = "sent"
        except Exception as exc:
            log.status = "failed"
            log.error_detail = str(exc)
            db.add(log)
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

        db.add(log)
    return {"sent": charge_id, "attempt": attempt}
