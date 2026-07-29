# ---------------------------------------------------------------------------
# Stage 1 — install dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Prevent pip from caching packages in ~/.cache/pip
ENV PIP_NO_CACHE_DIR=1

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---------------------------------------------------------------------------
# Stage 2 — runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Create a non-root user
RUN groupadd --system app && useradd --system --gid app --create-home app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Put the venv on PATH so uvicorn is found
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the application source needed at runtime
WORKDIR /home/app
COPY --chown=app:app app/ ./app/
COPY --chown=app:app frontend/ ./frontend/

# Ensure the data directory exists and is writable by the app user
RUN mkdir -p /home/app/app/data && chown app:app /home/app/app/data

# Switch to the non-root user
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
