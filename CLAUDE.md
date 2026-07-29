# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the development server (with auto-reload)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Run all tests
python -m pytest tests/ -v

# Run a single test
python -m pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body -v

# Run tests with warnings as errors
python -m pytest tests/ -v -W error

# Run the Part A verification script (standalone, no server needed)
python tests/verify_a.py
```

On Windows, use `python` (or `py -m` if preferred). The virtual environment is at `venv/` and must be activated before running commands outside the project's VS Code terminal.

## Architecture

This is a minimal Task Tracker REST API built with FastAPI, with a vanilla JS Kanban board frontend. It is a learning project for the AI-Assisted Coding module.

**Three-layer architecture — routes must never access the JSON file directly:**

```
main.py (API routes + wiring)
    ↓
TaskService (app/services/task_service.py)  — orchestrates business rules
    ↓
JsonTaskRepository (app/repositories/task_repository.py)  — persistence
    ↓
app/data/tasks.json
```

### Key files

| File | Role |
|------|------|
| `app/main.py` | FastAPI app creation, CORS middleware, dependency wiring, and all `/tasks` route handlers |
| `app/models/task.py` | Pydantic models: `TaskCreate`, `TaskUpdate`, `TaskResponse`, and enums `TaskStatus`/`TaskPriority` |
| `app/services/task_service.py` | `TaskService` — thin orchestration layer; validates status transitions via `business_rules.py`, delegates persistence to the repository |
| `app/repositories/task_repository.py` | `JsonTaskRepository` — reads/writes the full JSON file atomically (temp file + `os.replace`); thread-safe via `threading.Lock` |
| `app/business_rules.py` | `validate_status_transition()` — the single place for valid status transition rules |
| `app/api/routes/health.py` | `GET /health` endpoint (separate router) |
| `frontend/index.html` | Single-file Kanban board (vanilla HTML/CSS/JS); served by `GET /` as a `FileResponse` |
| `tests/conftest.py` | Pytest fixtures: autouse `_reset_storage` (clears JSON file before/after each test), `client` (TestClient), `created_task` |

### Request flow

1. FastAPI validates the request body against the Pydantic model (`TaskCreate` or `TaskUpdate`).
2. `main.py` route handler calls the `TaskService` method.
3. `TaskService` validates business rules (e.g., status transitions) and delegates to `JsonTaskRepository`.
4. `JsonTaskRepository` reads `app/data/tasks.json`, applies changes, and writes atomically.

### Pydantic model rules

- Both `TaskCreate` and `TaskUpdate` use `extra="forbid"` — unknown fields return 422.
- `TaskCreate.title` is required, stripped of whitespace, and must be non-blank and ≤200 chars.
- `TaskCreate` defaults: `status=ToDo`, `priority=Medium`, `description=""`, `tags=[]`.
- `TaskUpdate` has all optional fields; only explicitly-set fields are applied (`exclude_unset=True`).
- Tags are cleaned in both models: whitespace trimmed, empty tags removed, duplicates removed (case-sensitive).
- `TaskResponse` includes `id`, `created_at`, and `updated_at` — these are set by the repository, not by request input.

### Status transitions (`app/business_rules.py`)

Valid transitions: ToDo→InProgress, InProgress→Done, Done→InProgress, and same-status for idempotency. ToDo→Done is **invalid** (must go through InProgress first). The service raises HTTP 422 on invalid transitions.

### Repository patterns

- `JsonTaskRepository._read_all()` returns a `Dict[str, dict]` keyed by task ID. Returns `{}` on missing file, empty file, or invalid JSON.
- `_write_all()` uses `tempfile.mkstemp` + `os.replace` for atomic writes, guarded by `threading.Lock`.
- `_reset()` clears all data — exposed for tests only via the `repo` property on the service.
- Task IDs are generated with `uuid4().hex`.

### Frontend (`frontend/index.html`)

- Single-file Kanban board with three columns: ToDo, InProgress, Done.
- Hardcoded to `http://localhost:8000` as the API base URL.
- Supports drag-and-drop between columns (PATCH status), inline editing via modal, overdue filtering.
- Overdue = `due_date < today` AND `status != Done`. Calculated client-side.

### Tests

- Uses `fastapi.testclient.TestClient` (imported from `app.main:app`).
- `conftest.py` provides auto-reset of the JSON store before and after every test — tests are isolated.
- The `created_task` fixture POSTs a task and returns the response JSON for tests that need an existing task.
- `tests/verify_a.py` is a standalone script that validates Pydantic model rules without a running server.

### Project constraints (from ADRs)

- No new Backend endpoints for overdue filtering or tags — filtering happens client-side.
- No separate Tag model/table — tags are plain string lists.
- No time-of-day deadlines or timezone handling.
- Due dates are `date` (ISO YYYY-MM-DD), not `datetime`.
