# Architecture C

## 1. What it does

The application defines a FastAPI service titled `Task Tracker API`. It serves a frontend HTML file from `GET /` using `FileResponse("frontend/index.html")` and exposes REST endpoints for creating, listing, reading, updating, and deleting tasks under `/tasks`.

The app loads environment variables with `load_dotenv()` and reads `APP_ENV`, defaulting to `development`, for the API description. It also enables CORS for several local development origins and includes a health router from `app.api.routes.health`. The behavior of the health endpoint is not visible from the files I read.

Task behavior is routed through a `TaskService`, which is constructed with `JsonTaskRepository("app/data/tasks.json")`. The internal service and repository behavior is not visible from the files I read.

## 2. Data model

The route layer imports `TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskStatus`, and `TaskPriority` from `app.models`. The field definitions, enum values, and validation rules are not visible from the files I read because `app/models.py` was not present at the requested path.

From route annotations and docstrings, task creation accepts a `TaskCreate` payload and returns a `TaskResponse`. The create route documentation says `title` is required and that created task responses include server-assigned `id`, `created_at`, and `updated_at` fields. The update route accepts `TaskUpdate` and applies partial updates. Exact model defaults and constraints are not visible from the files I read.

## 3. Request flow when a user creates a task

1. A client sends `POST /tasks` with a JSON body.
2. FastAPI validates the request body as `TaskCreate`.
3. The `create_task` route handler receives the validated payload.
4. The route calls `service.create_task(payload)`.
5. The service was created from `TaskService(repo)`, where `repo` is `JsonTaskRepository("app/data/tasks.json")`.
6. The created task is returned as a `TaskResponse` with HTTP status `201 Created`.

The exact logic used to assign IDs, timestamps, defaults, validation errors, or persistence writes is not visible from the files I read.

## 4. Key files

`app/main.py`: Defines the FastAPI application, CORS configuration, frontend route, task routes, health router inclusion, and wiring between `TaskService` and `JsonTaskRepository`.

`app/models.py`: not visible from the files I read.

`app/storage.py`: not visible from the files I read.

Additional imported modules such as `app.repositories`, `app.services`, and `app.api.routes.health` are referenced by `app/main.py`, but their contents are not visible from the files I read.

## 5. Conventions

Routes are thin and delegate task operations to `service`. The service is initialized once at module import time with a repository instance.

Task endpoints use FastAPI response models and tags. `POST /tasks` explicitly returns `201 Created`; `DELETE /tasks/{task_id}` explicitly returns `204 No Content`.

The frontend is served by the backend from `frontend/index.html`. The persistence path configured in `app/main.py` is `app/data/tasks.json`.

More detailed conventions for model validation, storage format, error handling, and task status transitions are not visible from the files I read.
