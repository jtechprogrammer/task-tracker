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
    return FileResponse("frontend/index.html")


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    return service.create_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def get_all_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[TaskResponse]:
    return service.list_tasks(status=status, priority=priority)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def get_task(task_id: str) -> TaskResponse:
    return service.get_task(task_id)


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    return service.update_task(task_id, payload)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: str) -> None:
    service.delete_task(task_id)
    return None