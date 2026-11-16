# Importa todos os modelos para que o SQLAlchemy resolva os relacionamentos
# declarados por nome (ex.: relationship("MessageLog")) em qualquer ponto de entrada.
from app.models import user, client, charge, payment, message_log, resend_config  # noqa: F401
