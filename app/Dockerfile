FROM python:3.12-slim AS base
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# O código usa imports "app.*", então ele fica em /srv/app e o processo roda em /srv
COPY pyproject.toml /tmp/deps/pyproject.toml

FROM base AS development
RUN pip install --no-cache-dir "/tmp/deps[dev]"
COPY . ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
RUN pip install --no-cache-dir /tmp/deps
COPY . ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
