FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

RUN groupadd --system app && useradd --system --gid app --home-dir /home/app --create-home app

WORKDIR /home/app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app/ ./app/
COPY --chown=app:app frontend/ ./frontend/

RUN mkdir -p app/data && chown -R app:app app/data

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
