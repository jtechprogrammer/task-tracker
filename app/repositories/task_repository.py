"""JSON file repository for task persistence."""

import json
import os
import tempfile
from threading import Lock
from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime, timezone
from pathlib import Path

from app.models import TaskCreate, TaskResponse, TaskStatus, TaskPriority, TaskUpdate


class JsonTaskRepository:
    """Persists tasks to a JSON file on disk.

    Reads the full file into memory on each operation and writes
    atomically (temp file + rename) to avoid data loss.
    A threading lock guards concurrent access within the same process.
    """

    def __init__(self, file_path: str = "app/data/tasks.json") -> None:
        self._file_path = Path(file_path)
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_all(self) -> Dict[str, dict]:
        """Return all task dicts keyed by ID.  Empty dict when the file
        does not exist or contains invalid JSON."""
        if not self._file_path.exists():
            return {}
        try:
            text = self._file_path.read_text(encoding="utf-8")
        except OSError:
            return {}
        if not text.strip():
            return {}
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            return {}
        if not isinstance(raw, list):
            return {}
        return {item["id"]: item for item in raw if isinstance(item, dict) and "id" in item}

    def _write_all(self, tasks: Dict[str, dict]) -> None:
        """Atomically write the full task collection to disk."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        data = list(tasks.values())
        with self._lock:
            json_text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            # Atomic write: write to a temp file in the same directory, then replace
            tmp_fd, tmp_name = tempfile.mkstemp(
                dir=self._file_path.parent, suffix=".tmp"
            )
            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                    f.write(json_text)
                os.replace(tmp_name, str(self._file_path))
            except Exception:
                # Clean up temp file on failure
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
                raise

    def _dict_to_response(self, d: dict) -> TaskResponse:
        """Convert a raw dict back to a TaskResponse model."""
        return TaskResponse.model_validate(d)

    def _response_to_dict(self, task: TaskResponse) -> dict:
        """Convert a TaskResponse to a JSON-safe dict."""
        return task.model_dump(mode="json")

    # ------------------------------------------------------------------
    # Public API (mirrors the old storage.py surface)
    # ------------------------------------------------------------------

    def add(self, payload: TaskCreate) -> TaskResponse:
        task_id = uuid4().hex
        now = datetime.now(timezone.utc)
        task = TaskResponse(
            id=task_id,
            title=payload.title,
            description=payload.description or "",
            status=payload.status,
            priority=payload.priority,
            assignee=payload.assignee,
            due_date=payload.due_date,
            tags=payload.tags,
            created_at=now,
            updated_at=now,
        )
        tasks = self._read_all()
        tasks[task_id] = self._response_to_dict(task)
        self._write_all(tasks)
        return task

    def get_all(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[TaskResponse]:
        tasks = self._read_all()
        results = [self._dict_to_response(d) for d in tasks.values()]
        if status is not None:
            results = [t for t in results if t.status == status]
        if priority is not None:
            results = [t for t in results if t.priority == priority]
        return results

    def get_by_id(self, task_id: str) -> Optional[TaskResponse]:
        tasks = self._read_all()
        d = tasks.get(task_id)
        if d is None:
            return None
        return self._dict_to_response(d)

    def update(self, task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
        tasks = self._read_all()
        d = tasks.get(task_id)
        if d is None:
            return None
        existing = self._dict_to_response(d)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return existing
        updated = existing.model_copy(update=updates)
        updated = updated.model_copy(update={"updated_at": datetime.now(timezone.utc)})
        tasks[task_id] = self._response_to_dict(updated)
        self._write_all(tasks)
        return updated

    def delete(self, task_id: str) -> bool:
        tasks = self._read_all()
        if task_id not in tasks:
            return False
        del tasks[task_id]
        self._write_all(tasks)
        return True

    def _reset(self) -> None:
        """Clear all tasks — used by the test fixtures."""
        self._write_all({})
