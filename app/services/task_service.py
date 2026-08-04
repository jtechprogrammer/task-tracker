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
        """Initialize the service with a task repository.

        Args:
            repository: A repository object that implements the same
                interface as ``JsonTaskRepository`` (``add``,
                ``get_all``, ``get_by_id``, ``update``, ``delete``).
        """
        self._repo = repository

    # ------------------------------------------------------------------
    # Task CRUD
    # ------------------------------------------------------------------

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        """Create a new task and persist it.

        Args:
            payload: Validated ``TaskCreate`` body.

        Returns:
            TaskResponse: The persisted task with server-assigned fields.
        """
        return self._repo.add(payload)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> list[TaskResponse]:
        """List tasks with optional status/priority filters.

        Args:
            status: Filter by workflow status, or ``None`` for all.
            priority: Filter by priority, or ``None`` for all.

        Returns:
            list[TaskResponse]: Matching tasks (empty list when none
            match).
        """
        return self._repo.get_all(status=status, priority=priority)

    def get_task(self, task_id: str) -> TaskResponse:
        """Get a single task by ID.

        Args:
            task_id: The hex task ID.

        Returns:
            TaskResponse: The matching task.

        Raises:
            HTTPException: 404 if the task does not exist.
        """
        task = self._repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task

    def update_task(self, task_id: str, payload: TaskUpdate) -> TaskResponse:
        """Update an existing task with partial data.

        Args:
            task_id: The hex task ID.
            payload: ``TaskUpdate`` body; only explicitly-set fields are
                applied.

        Returns:
            TaskResponse: The updated task.

        Raises:
            HTTPException: 404 if the task does not exist.
            HTTPException: 422 if a status transition is invalid.
        """
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
        """Delete a task by ID.

        Args:
            task_id: The hex task ID.

        Returns:
            None

        Raises:
            HTTPException: 404 if the task does not exist.
        """
        if not self._repo.delete(task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

    @property
    def repo(self):
        """Expose the backing repository so test fixtures can call _reset()."""
        return self._repo
