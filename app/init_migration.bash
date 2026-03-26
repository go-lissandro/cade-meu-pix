# Inicializar (apenas uma vez)
alembic init alembic

# Criar migration
alembic revision --autogenerate -m "initial schema"

# Aplicar ao banco
alembic upgrade head