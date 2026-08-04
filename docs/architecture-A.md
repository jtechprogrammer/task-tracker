# Task Tracker Architecture

## 1. What the app does

Task Tracker is a small FastAPI application with a vanilla HTML/CSS/JavaScript Kanban frontend. Users can create, view, update, drag between workflow columns, filter overdue tasks, and delete tasks; task data is persisted locally in a JSON file.

## 2. Data model

The main entity is `Task`. A task has server-managed `id`, `created_at`, and `updated_at` fields, plus user-controlled `title`, `description`, `status`, `priority`, `assignee`, `due_date`, and `tags`. Valid statuses are `ToDo`, `InProgress`, and `Done`; valid priorities are `Low`, `Medium`, and `High`.

## 3. Request flow

When a user creates a task in the frontend, `frontend/index.html` validates the title, builds a JSON request, and sends `POST /tasks` to the FastAPI backend. `app/main.py` receives the request as a `TaskCreate` model, delegates to `TaskService`, and the service calls `JsonTaskRepository.add()`. The repository generates a UUID-style hex ID plus UTC timestamps, reads the existing task list from `app/data/tasks.json`, appends the new task, atomically writes the file, and returns a `TaskResponse` back through the service and route.

## 4. Key files

- `app/main.py` - FastAPI app setup, CORS, frontend serving, task routes, service/repository wiring.
- `app/models/task.py` - Pydantic task schemas, status/priority enums, validation rules.
- `app/services/task_service.py` - Service layer for task CRUD and status-transition enforcement.
- `app/repositories/task_repository.py` - JSON-file persistence, ID/timestamp generation, atomic writes.
- `app/business_rules.py` - Allowed task status transitions and 422 error behavior.
- `app/api/routes/health.py` - Health endpoint router.
- `frontend/index.html` - Single-file Kanban UI and browser-side API calls.
- `tests/test_tasks.py` - Endpoint tests for create/list/get/update/delete and validation behavior.
- `tests/conftest.py` - TestClient fixture and repository reset fixture.
- `app/data/tasks.json` - Local JSON task store.

## 5. Conventions

Routes should go through the service and repository layers rather than reading `app/data/tasks.json` directly. Pydantic models reject unknown fields, validate enum values, trim task titles, reject blank or over-200-character titles, validate due dates, and clean tags by trimming, dropping empty values, and removing duplicates. Missing tasks return `404`; validation errors and invalid status transitions return `422`; successful deletes return `204` with no body. The frontend is served by `GET /` but calls the API using a hardcoded `http://localhost:8000` base URL. Overdue filtering is calculated client-side.

## 6. Not visible or assumptions

No database, authentication, authorization, pagination, or comment system is visible. No separate `app/storage.py` file is visible; persistence is handled by `app/repositories/task_repository.py`. The README appears older than the implementation because it says task CRUD is not implemented, while the code and tests show task CRUD endpoints exist. Docker behavior and production deployment conventions were not fully verified from this architecture pass.
