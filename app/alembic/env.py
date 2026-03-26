from app.core.config import settings
from app.models.base import Base
# Importar todos os models para que o Alembic os detecte
from app.models import user, client, charge, payment, message_log, resend_config

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata