# Architecture - Strategy B

## 1. What it does

Task Tracker is a small FastAPI application for a local AI-assisted coding course project. It serves a vanilla HTML/CSS/JavaScript Kanban board at `GET /` and exposes a REST API for task management.

The backend supports:

- `GET /health`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

`GET /tasks` can filter by `status` and `priority`. Task data is persisted as a JSON list in `app/data/tasks.json`. The project is local-learning oriented; authentication is not implemented.

## 2. Data model

Task schemas are defined in `app/models/task.py`.

A task create request accepts:

- `title`
- `description`
- `status`
- `priority`
- `assignee`
- `due_date`
- `tags`

Task responses include those fields plus server-managed fields:

- `id`
- `created_at`
- `updated_at`

`id` values are generated with `uuid4().hex` in `app/repositories/task_repository.py`. Timestamps are generated in UTC.

Valid statuses are `ToDo`, `InProgress`, and `Done`. New tasks default to `ToDo`.

Valid priorities are `Low`, `Medium`, and `High`. New tasks default to `Medium`.

Validation is handled by Pydantic models. Task titles are trimmed, required, non-blank, and limited to 200 characters. Unknown request fields are rejected. `due_date` is optional and validated as a date. Tags default to an empty list, are trimmed, have empty values removed, and have duplicate values removed using case-sensitive comparison.

## 3. Request flow when a user creates a task

1. A browser or API client sends `POST /tasks` with a JSON body.
2. FastAPI validates the body against `TaskCreate` from `app/models/task.py`.
3. The `create_task` route in `app/main.py` receives the validated payload.
4. The route delegates to `TaskService.create_task()` in `app/services/task_service.py`.
5. The service delegates persistence to `JsonTaskRepository.add()` in `app/repositories/task_repository.py`.
6. The repository generates the task ID and UTC timestamps, builds a `TaskResponse`, reads the current JSON file, adds the new task, and writes the full collection back atomically using a temporary file plus `os.replace`.
7. FastAPI serializes the returned `TaskResponse` and sends `201 Created`.

Routes should not access `app/data/tasks.json` directly. The intended flow is:

```text
app/main.py route
    -> TaskService
    -> JsonTaskRepository
    -> app/data/tasks.json
```

## 4. Key files

- `app/main.py`: Creates the FastAPI app, configures CORS, serves `frontend/index.html`, wires the repository and service, and defines task CRUD routes.
- `app/services/task_service.py`: Coordinates task operations, handles missing-task `404` responses, and calls status-transition validation during updates.
- `app/repositories/task_repository.py`: Reads and writes the JSON task store, generates IDs, assigns timestamps, filters task lists, and exposes `_reset()` for tests.
- `app/models/task.py`: Defines task enums and Pydantic schemas for create, update, and response bodies.
- `app/business_rules.py`: Defines allowed task status transitions and raises `422` for invalid transitions such as `ToDo -> Done`.
- `app/api/routes/health.py` and `app/models/health.py`: Define the health endpoint and its response model.
- `app/data/tasks.json`: Stores persisted task records as a JSON list.
- `frontend/index.html`: Implements the single-file Kanban board and calls the task API.
- `tests/`: Contains API tests and fixtures that exercise current task behavior.

`app/models_legacy.py` is an older model file and is not part of the current public model exports.

## 5. Conventions

- Keep route handlers thin; put orchestration in services and persistence in repositories.
- Do not have routes read or write `app/data/tasks.json` directly.
- Put request/response shape validation in Pydantic models.
- Put cross-cutting workflow rules in `app/business_rules.py` and invoke them from the service layer.
- Reject unknown request fields with `extra="forbid"`.
- Apply partial updates with only explicitly provided fields.
- Use UTC timestamps for server-managed datetime fields.
- Use JSON-file persistence for this course project; the repository currently reads the full file and writes the full collection.
- Treat missing, empty, invalid, or non-list task storage as an empty task collection.
- Keep frontend status values aligned with backend enum values: `ToDo`, `InProgress`, and `Done`.
- Do not expose secrets or inspect `.env` unless there is a clear, explicit reason.
