from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
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
