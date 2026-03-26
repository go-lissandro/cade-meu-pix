FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN pip install uv

FROM base AS development
COPY pyproject.toml .
RUN uv pip install --system -e ".[dev]"
COPY . .

FROM base AS production
COPY pyproject.toml .
RUN uv pip install --system --no-dev .
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]