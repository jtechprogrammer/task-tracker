import os

from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import TaskCreate, TaskResponse, TaskStatus, TaskPriority, TaskUpdate
from app.repositories import JsonTaskRepository
from app.services import TaskService

from app.api.routes.health import router as health_router


load_dotenv()

app_environment = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Task Tracker API",
    description=(
        "A minimal FastAPI REST API for the Module 1 Task Tracker "
        f"learning project. Environment: {app_environment}."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)

# ---------------------------------------------------------------------------
# Wiring — instantiate the persistence layer and the service
# ---------------------------------------------------------------------------

repo = JsonTaskRepository("app/data/tasks.json")
service = TaskService(repo)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=FileResponse, include_in_schema=False)
def get_frontend_index() -> FileResponse:
    """Serve the Kanban board frontend SPA.

    Returns:
        FileResponse: The ``frontend/index.html`` file.

    Example:
        ``GET /`` → 200 (HTML page)
    """
    return FileResponse("frontend/index.html")


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload: The task to create. ``title`` is required; other fields
            default as defined by the ``TaskCreate`` model.

    Returns:
        TaskResponse: The created task with server-assigned ``id``,
        ``created_at``, and ``updated_at``.

    Raises:
        HTTPException: 422 if the request body fails Pydantic validation
            (e.g. blank title, unknown fields, title >200 chars).

    Example:
        ``POST /tasks`` with ``{"title": "Buy milk"}``
        → 201 with full ``TaskResponse`` body.
    """
    return service.create_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def get_all_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status and/or priority.

    Args:
        status: If provided, return only tasks with this status.
        priority: If provided, return only tasks with this priority.

    Returns:
        list[TaskResponse]: All matching tasks (empty list when none
        match).

    Example:
        ``GET /tasks?status=ToDo&priority=High``
        → 200 with a JSON array of ``TaskResponse`` objects.
    """
    return service.list_tasks(status=status, priority=priority)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def get_task(task_id: str) -> TaskResponse:
    """Get a single task by ID.

    Args:
        task_id: The hex task ID (e.g. ``"a1b2c3d4..."``).

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task is found with the given ID.

    Example:
        ``GET /tasks/a1b2c3d4e5f6...``
        → 200 with that task's ``TaskResponse`` body.
    """
    return service.get_task(task_id)


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update an existing task.

    Args:
        task_id: The hex task ID.
        payload: A ``TaskUpdate`` body; only explicitly-set fields are
            applied. Unknown fields are rejected.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task is found with the given ID.
        HTTPException: 422 if a status transition is invalid (e.g.
            ``ToDo → Done``) or if the request body fails Pydantic
            validation.

    Example:
        ``PATCH /tasks/a1b2c3...`` with ``{"status": "Done"}``
        → 200 with the updated ``TaskResponse`` body.
    """
    return service.update_task(task_id, payload)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: str) -> None:
    """Delete a task by ID.

    Args:
        task_id: The hex task ID.

    Returns:
        None: Responds with 204 No Content on success.

    Raises:
        HTTPException: 404 if no task is found with the given ID.

    Example:
        ``DELETE /tasks/a1b2c3d4...``
        → 204 No Content with empty body.
    """
    service.delete_task(task_id)
    return None