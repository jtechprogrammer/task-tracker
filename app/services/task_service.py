"""Task service — orchestrates business rules and persistence."""

from typing import Optional

from fastapi import HTTPException, status

from app.models import TaskCreate, TaskResponse, TaskStatus, TaskPriority, TaskUpdate
from app.business_rules import validate_status_transition


class TaskService:
    """Thin service layer that wraps a repository and enforces business rules.

    The service does NOT know about the storage medium — it only calls
    the repository interface, making it easy to swap implementations.
    """

    def __init__(self, repository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # Task CRUD
    # ------------------------------------------------------------------

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        return self._repo.add(payload)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> list[TaskResponse]:
        return self._repo.get_all(status=status, priority=priority)

    def get_task(self, task_id: str) -> TaskResponse:
        task = self._repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task

    def update_task(self, task_id: str, payload: TaskUpdate) -> TaskResponse:
        existing = self._repo.get_by_id(task_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        if payload.status is not None:
            validate_status_transition(existing.status, payload.status)

        updated = self._repo.update(task_id, payload)
        # Should not happen (we already checked existence under lock-free
        # conditions), but guard anyway.
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return updated

    def delete_task(self, task_id: str) -> None:
        if not self._repo.delete(task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

    @property
    def repo(self):
        """Expose the backing repository so test fixtures can call _reset()."""
        return self._repo
