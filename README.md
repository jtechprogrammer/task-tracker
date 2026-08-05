# Task Tracker API

A minimal Task Tracker REST API built with Python and FastAPI.

This project is part of the AI-Assisted Coding Module 1 learning work. Its current purpose is to establish the project structure and verify that the FastAPI application runs correctly.

## Current scope

The current skeleton includes:

- A FastAPI application
- Environment variable loading with `python-dotenv`
- A Pydantic health response model
- A `GET /health` endpoint
- Packages for API routes, services, repositories, and models
- An empty JSON file for future task storage
- Interactive Swagger API documentation

Task CRUD endpoints are not implemented yet.

## Architecture

The application will use the following layers:

```text
API routes
    ↓
Task service
    ↓
JSON task repository
    ↓
app/data/tasks.json
```

API routes must not access the JSON file directly. Future task operations will go through the service and repository layers.

## Requirements

- Python 3.10 or newer
- `pip`

Check your Python installation:

```bash
python --version
```

On Linux or macOS, you may need to use:

```bash
python3 --version
```

## Setup on Linux or macOS

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Create the local environment file:

```bash
cp .env.example .env
```

## Setup on Windows PowerShell

Create a virtual environment:

```powershell
py -m venv venv
```

Allow script execution for the current PowerShell process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

## Run the development server

Run this command from the project root:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

The `--reload` option automatically restarts the development server when Python files change. It is intended for local development only.

## Test the health endpoint

Using Bash:

```bash
curl http://127.0.0.1:8000/health
```

Using Windows PowerShell:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected response shape:

```json
{
  "status": "ok",
  "timestamp": "2026-07-20T06:30:00.000000Z"
}
```

The timestamp value will be different for every request.

## Swagger documentation

Open the following URL in a browser:

```text
http://127.0.0.1:8000/docs
```

Swagger UI allows you to inspect and test the API endpoints interactively.

Alternative ReDoc documentation is available at:

```text
http://127.0.0.1:8000/redoc
```

## Stop the server

Press:

```text
Ctrl+C
```

## Installed dependency versions

The initial `requirements.txt` does not pin dependency versions.

After installing the dependencies, you can record the exact installed versions with:

```bash
python -m pip freeze > requirements.lock.txt
```

## Final Project

Branch reviewed: `final-project`

### What This Submission Demonstrates

- The existing Task Tracker still runs inside the intended course scope.
- CI runs the pytest suite on push and pull request.
- The Docker image builds and runs with `/health` returning HTTP 200.
- AI review, security, and ownership evidence are documented in `docs/`.

### How to Run Locally

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000/` for the Kanban board or `http://127.0.0.1:8000/health` for the health check.

### How to Run Tests

```bash
python -m pytest tests -v
```

### How to Run with Docker

```bash
docker build -t task-tracker-final .
docker run --rm -p 8000:8000 task-tracker-final
curl http://127.0.0.1:8000/health
```

### Evidence Files

- [docs/release-evidence.md](docs/release-evidence.md) — baseline, CI, Docker, and documentation-vs-reality checks.
- [docs/final-ai-review.md](docs/final-ai-review.md) — AGENTS.md guardrail check, AI code review and security mini-logs, manual security check, rejected AI output, ownership statement.
- [docs/ai-playbook.md](docs/ai-playbook.md) — personal rules for working with AI.

### AI Assistance Summary

AI helped draft or review: CI/Docker cleanup, README wording, and a read-only code and security review of `app/repositories/task_repository.py`, `app/business_rules.py`, and `app/main.py`.

I verified the work by: running the full pytest suite (`34 passed`), building and running the Docker image and checking `/health` and non-root/no-secrets behavior directly, and reading every flagged file and line myself before accepting or rejecting a finding.

One AI suggestion I rejected: collapsing the multi-stage `Dockerfile` into a single stage "to simplify it" — this would have shipped build tooling in the runtime image and undone the non-root user setup, so the two-stage build was kept as-is (see `docs/final-ai-review.md`).