# syntax=docker/dockerfile:1

# --- build stage: install dependencies into a venv ------------------------
FROM python:3.12-slim AS build
WORKDIR /app
COPY app/requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# --- runtime stage: minimal, non-root ------------------------------------
FROM python:3.12-slim AS runtime

# Create an unprivileged user to run the service.
RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=dev

WORKDIR /srv
COPY app/ ./app/

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz').status==200 else 1)"

# 2 workers is plenty for a demo service.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app.app:app"]
