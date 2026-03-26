# 1. Clone e configure
cp .env.example .env
# Edite .env com suas credenciais

# 2. Suba os serviços
docker compose up -d postgres redis

# 3. Instale as dependências (com uv ou pip)
uv pip install -e ".[dev]"

# 4. Rode as migrations
alembic upgrade head

# 5. Suba a API
uvicorn app.main:app --reload

# 6. Em outro terminal, suba os workers
celery -A app.workers.celery_app worker -Q whatsapp,email,resend,status --loglevel=info &
celery -A app.workers.celery_app beat --loglevel=info

# Ou tudo via Docker Compose
docker compose up --build