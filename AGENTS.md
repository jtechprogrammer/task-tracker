# AGENTS.md

## Project Summary

This repository contains a small Task Tracker application for the AI-Assisted Coding course modules. The backend is a FastAPI REST API with task CRUD endpoints, a health endpoint, and JSON-file persistence. The frontend is a single-file vanilla HTML/CSS/JavaScript Kanban board served by the backend at `GET /`.

The current architecture is:

```text
API routes in app/main.py
    -> TaskService in app/services/task_service.py
    -> JsonTaskRepository in app/repositories/task_repository.py
    -> app/data/tasks.json
```

Routes should go through the service and repository layers. Do not have route handlers access `app/data/tasks.json` directly.

## Tech Stack

- Python 3.10 or newer is documented in `README.md`.
- The Dockerfile uses `python:3.11-slim`.
- FastAPI provides the API.
- Uvicorn runs the development server.
- Pydantic validates request and response models.
- python-dotenv loads local environment variables.
- The frontend is plain HTML, CSS, and JavaScript in `frontend/index.html`.
- Persistence is a JSON file at `app/data/tasks.json`.

## Supported Commands

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the development server from the repository root:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

Check the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Run the test suite, as shown by CI:

```bash
pytest -v
```

Run the test suite with the Python module form, as shown in `CLAUDE.md`:

```bash
python -m pytest tests/ -v
```

Run the standalone Part A verification script:

```bash
python tests/verify_a.py
```

Docker build and run commands are not confirmed in repository docs. The Dockerfile exists and its container command runs:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Business Rules Visible in Code

### Task Fields

Task creation accepts these fields:

- `title`
- `description`
- `status`
- `priority`
- `assignee`
- `due_date`
- `tags`

Task responses include server-managed fields:

- `id`
- `created_at`
- `updated_at`

Task IDs are generated with `uuid4().hex`. Timestamps are generated in UTC.

### Statuses

Valid task statuses are:

- `ToDo`
- `InProgress`
- `Done`

New tasks default to `ToDo`.

### Priorities

Valid task priorities are:

- `Low`
- `Medium`
- `High`

New tasks default to `Medium`.

### Validation Rules

- `title` is required on create.
- `title` is stripped of surrounding whitespace.
- `title` must not be blank.
- `title` must not exceed 200 characters.
- Unknown request fields are rejected.
- Invalid enum values are rejected.
- `description` defaults to an empty string.
- `assignee` defaults to `None`.
- `due_date` is optional and validated as a date.
- Invalid due-date values return validation errors.
- `tags` defaults to an empty list.
- Tags are stripped of surrounding whitespace.
- Empty tags are removed.
- Duplicate tags are removed.
- Tag comparison is case-sensitive, so `frontend` and `Frontend` are distinct.
- `tags: null` is rejected on update.
- Partial updates only apply explicitly provided fields.

### Status Transitions

Allowed status transitions are:

- `ToDo -> InProgress`
- `InProgress -> Done`
- `Done -> InProgress`
- `ToDo -> ToDo`
- `InProgress -> InProgress`
- `Done -> Done`

`ToDo -> Done` is invalid. Invalid transitions return HTTP 422.

### API Behavior

Visible endpoints include:

- `GET /`
- `GET /health`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

`GET /tasks` supports optional `status` and `priority` filters.

Missing tasks return HTTP 404.

Deleting an existing task returns HTTP 204 with no response body.

### Persistence Rules

Tasks are stored as a JSON list in `app/data/tasks.json`.

The repository reads the full JSON file for operations and writes updates atomically using a temporary file plus `os.replace`.

If the JSON file is missing, empty, invalid JSON, or not a list, repository reads return an empty task collection.

### Frontend Rules

The frontend is served from `frontend/index.html`.

The frontend API base URL is hardcoded as:

```javascript
http://localhost:8000
```

The Kanban columns use these statuses:

- `ToDo`
- `InProgress`
- `Done`

The frontend calculates overdue tasks client-side. A task is overdue when:

- it has a `due_date`
- the due date is earlier than the browser's current local date
- the task status is not `Done`

The overdue filter is client-side. A dedicated backend overdue endpoint is not confirmed.

## Module 5 Guardrails

- Docs-first: read `README.md`, relevant files in `docs/`, and the source files related to the request before proposing changes.
- Read-only by default: inspect, summarize, and propose before editing.
- One task per thread: keep each Codex task focused on one repository task or review topic.
- Do not change files under `app/` unless the user explicitly approves application-code changes.
- For Module 5 setup and governance tasks, prefer documentation-only updates unless the user clearly asks for implementation.

## Security and Governance Reminders

- Do not paste, expose, or commit secrets.
- Do not read or print `.env` unless the user explicitly asks and there is a clear reason.
- Use `.env.example` for documented environment variables.
- Do not run destructive commands such as recursive delete, `git reset --hard`, or force-push unless the user explicitly requests and approves them.
- Do not invent findings, commands, endpoints, business rules, or test results.
- If something is not visible in the repository, mark it as `not confirmed`.
- Cite the files that support claims, especially for reviews, business rules, and architecture notes.
- Keep edits narrow and avoid unrelated refactors.
- Before changing behavior, identify affected tests or state that test coverage is not confirmed.
