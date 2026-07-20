import os

from dotenv import load_dotenv
from fastapi import FastAPI

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