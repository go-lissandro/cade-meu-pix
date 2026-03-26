backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── clients.py
│   │   │   │   ├── charges.py
│   │   │   │   ├── payments.py
│   │   │   │   └── dashboard.py
│   │   │   └── router.py
│   │   └── deps.py           # Injeção de dependências (DB, usuário atual)
│   ├── core/
│   │   ├── config.py          # Settings via pydantic-settings
│   │   ├── security.py        # JWT, hashing
│   │   └── database.py        # Engine SQLAlchemy + sessão
│   ├── models/                # Modelos SQLAlchemy (ORM)
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── charge.py
│   │   ├── payment.py
│   │   ├── message_log.py
│   │   └── resend_schedule.py
│   ├── schemas/               # Schemas Pydantic (request/response)
│   │   ├── client.py
│   │   ├── charge.py
│   │   └── payment.py
│   ├── repositories/          # Acesso a dados (padrão Repository)
│   │   ├── base.py
│   │   ├── client_repo.py
│   │   └── charge_repo.py
│   ├── services/              # Regras de negócio
│   │   ├── charge_service.py
│   │   ├── payment_service.py
│   │   └── notification_service.py
│   ├── workers/               # Celery app + configuração
│   │   ├── celery_app.py
│   │   └── beat_schedule.py
│   ├── tasks/                 # Tarefas Celery
│   │   ├── whatsapp_task.py
│   │   ├── email_task.py
│   │   ├── resend_task.py
│   │   └── status_task.py
│   ├── integrations/          # Clientes de APIs externas
│   │   ├── whatsapp.py
│   │   └── email_provider.py
│   └── utils/
│       ├── message_builder.py # Monta o texto das cobranças
│       └── date_utils.py
├── alembic/                   # Migrations
├── tests/
├── Dockerfile
└── pyproject.toml