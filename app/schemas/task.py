
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PriorityType = Literal["low", "normal", "high", "urgent"]

StatusType = Literal[
    "pending",
    "in_progress",
    "completed"
]


class TaskCreate(BaseModel):

    title: str = Field(min_length=1, max_length=200)

    description: str | None = None

    category: str | None = None

    priority: PriorityType = "normal"

    status: StatusType = "pending"

    due_date: datetime | None = None


class TaskUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = None

    category: str | None = None

    priority: PriorityType | None = None

    status: StatusType | None = None

    due_date: datetime | None = None


class TaskResponse(BaseModel):

    id: int

    title: str

    description: str | None

    category: str | None

    priority: PriorityType

    status: StatusType

    due_date: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
