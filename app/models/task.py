from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    """Workflow status of a task.

    Values:
        TODO: Not yet started.
        IN_PROGRESS: Currently being worked on.
        DONE: Completed.
    """
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    """Importance level of a task.

    Values:
        LOW: Low urgency.
        MEDIUM: Default priority for new tasks.
        HIGH: Urgent / needs attention.
    """
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    """Schema for creating a new task.

    Attributes:
        title: Required. Trimmed, must be non-blank and ≤200 chars.
        description: Optional free-text description. Defaults to ``""``.
        status: Initial workflow status. Defaults to ``ToDo``.
        priority: Importance level. Defaults to ``Medium``.
        assignee: Optional person assigned. Defaults to ``None``.
        due_date: Optional ISO date (``YYYY-MM-DD``). Defaults to
            ``None``.
        tags: List of unique, non-empty string tags. Duplicates and empty
            strings are removed. Defaults to ``[]``.

    Raises:
        ValidationError: If ``title`` is blank or >200 chars, or if
            extra/unknown fields are present.
    """
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title", mode="before")
    def _strip_and_validate_title(cls, v):
        if not isinstance(v, str):
            raise TypeError("title must be a string")
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        if len(v) > 200:
            raise ValueError("title must not exceed 200 characters")
        return v

    @field_validator("tags")
    def _clean_tags(cls, v: list[str]) -> list[str]:
        seen: set[str] = set()
        cleaned: list[str] = []
        for tag in v:
            t = tag.strip()
            if not t:
                continue
            if t in seen:
                continue
            seen.add(t)
            cleaned.append(t)
        return cleaned


class TaskUpdate(BaseModel):
    """Schema for partially updating an existing task.

    All fields are optional; only explicitly-set fields are applied to
    the existing task (``exclude_unset=True``).

    Attributes:
        title: New title. Same validation as ``TaskCreate``.
        description: New description.
        status: New workflow status. Must be a valid transition (see
            ``validate_status_transition``).
        priority: New priority level.
        assignee: New assignee.
        due_date: New due date.
        tags: New tag list. Same cleaning as ``TaskCreate``.

    Raises:
        ValidationError: If extra/unknown fields are present, or if
            ``title`` fails validation when provided.
    """
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title", mode="before")
    def _strip_and_validate_title(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise TypeError("title must be a string")
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        if len(v) > 200:
            raise ValueError("title must not exceed 200 characters")
        return v

    @field_validator("tags")
    def _clean_tags(cls, v: list[str]) -> list[str]:
        seen: set[str] = set()
        cleaned: list[str] = []
        for tag in v:
            t = tag.strip()
            if not t:
                continue
            if t in seen:
                continue
            seen.add(t)
            cleaned.append(t)
        return cleaned


class TaskResponse(BaseModel):
    """Schema for a task returned by the API.

    Attributes:
        id: Server-assigned hex ID (UUID4 without dashes).
        title: Task title.
        description: Task description (always a string).
        status: Current workflow status.
        priority: Current priority level.
        assignee: Person assigned, or ``None``.
        due_date: ISO date string, or ``None``.
        tags: Cleaned list of tags.
        created_at: UTC datetime when the task was created.
        updated_at: UTC datetime of the last update.
    """
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
