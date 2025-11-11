from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, constr, validator

from .models import RoleEnum


# Agent output schema for strict JSON validation
class AgentTaskSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None  # ISO8601 string; app may parse later


class AgentResourceSchema(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    type: constr(strip_whitespace=True, min_length=1)
    url: Optional[str] = None


class AgentProjectSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=3) = Field(..., description="Project title")
    summary: constr(strip_whitespace=True, min_length=10) = Field(..., description="Short summary")
    departments: List[constr(strip_whitespace=True, min_length=2)] = Field(default_factory=list)
    stakeholders: List[constr(strip_whitespace=True, min_length=2)] = Field(default_factory=list)
    milestones: List[constr(strip_whitespace=True, min_length=2)] = Field(default_factory=list)
    tasks: List[AgentTaskSchema] = Field(default_factory=list)
    resources: List[AgentResourceSchema] = Field(default_factory=list)

    @validator("departments", "stakeholders", "milestones", pre=True)
    def _ensure_list(cls, v):  # noqa: N805
        if v is None:
            return []
        return v


# API request/response schemas
class CreateProjectRequest(BaseModel):
    instruction: constr(strip_whitespace=True, min_length=5)


class DepartmentOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: RoleEnum
    department_id: Optional[int] = None

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    assignee_id: Optional[int]
    due_date: Optional[datetime]

    class Config:
        from_attributes = True


class ResourceOut(BaseModel):
    id: int
    name: str
    type: str
    url: Optional[str]

    class Config:
        from_attributes = True


class CrewJobOut(BaseModel):
    id: int
    external_id: str
    status: str

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: int
    title: str
    summary: str
    department: Optional[DepartmentOut] = None
    tasks: List[TaskOut] = Field(default_factory=list)
    resources: List[ResourceOut] = Field(default_factory=list)
    crew_jobs: List[CrewJobOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CreateProjectResponse(BaseModel):
    project: ProjectOut
    crew_job_id: str


class AssignTaskRequest(BaseModel):
    user_id: int


class TokenPayload(BaseModel):
    sub: str
    role: RoleEnum
    exp: int


class AuthUser(BaseModel):
    id: int
    email: str
    role: RoleEnum
    department_id: Optional[int] = None


