FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

COPY . .

RUN uv sync \
    --frozen \
    --no-dev

RUN SECRET_KEY=build-only \
    DB_NAME=build \
    DB_USER=build \
    DB_PASSWORD=build \
    R2_ACCESS_KEY_ID=build-only \
    R2_SECRET_ACCESS_KEY=build-only \
    R2_BUCKET_NAME=build \
    R2_ENDPOINT_URL=https://build.invalid \
    R2_PUBLIC_HOST=build.invalid \
    .venv/bin/python manage.py compilemessages -l uk

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]