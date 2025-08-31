from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import uuid4


TaskStatus = Literal["backlog", "in_progress", "review", "complete"]


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    category: str
    status: TaskStatus = "backlog"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tasks: List[Task] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    id: str
    name: str
    description: str
    task_count: int
    created_at: datetime
    updated_at: datetime


class ProjectDetails(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    tasks: List[Task]
    task_stats: dict


class CreateProjectInput(BaseModel):
    name: str
    description: Optional[str] = ""


class CreateTaskInput(BaseModel):
    project_id: str
    description: str
    category: str


class UpdateTaskStatusInput(BaseModel):
    task_id: str
    status: TaskStatus


class OperationResponse(BaseModel):
    success: bool
    message: str