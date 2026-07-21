import os

from dotenv import load_dotenv
from fastapi import FastAPI, status
from app.models import TaskCreate, TaskResponse, TaskStatus, TaskPriority
from app import storage
from app.business_rules import validate_status_transition

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

app.include_router(health_router)

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def get_all_tasks(status: TaskStatus | None = None, priority: TaskPriority | None = None) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority)


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, status: TaskStatus) -> TaskResponse:
    task = storage.get_task(task_id)
    validate_status_transition(task.status, status)
    return storage.update_task_status(task_id, status)