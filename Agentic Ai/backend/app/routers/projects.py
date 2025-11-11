from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Base, Department, Project, Task, Resource, User, CrewJob, RoleEnum
from ..schemas import (
    CreateProjectRequest,
    CreateProjectResponse,
    ProjectOut,
    AssignTaskRequest,
    AuthUser,
)
from ..services.agents import AgentService
from ..services.crew_client import CrewAIClient

router = APIRouter()


# Simple auth skeleton
def get_current_user() -> AuthUser:
    # In production, decode JWT and fetch user; here we return a demo admin
    return AuthUser(id=1, email="admin@example.edu", role=RoleEnum.department_admin, department_id=None)


def require_role(user: AuthUser, allowed: List[RoleEnum]) -> None:
    if user.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.get("/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: AuthUser = Depends(get_current_user)) -> List[ProjectOut]:
    projects = db.query(Project).all()
    return projects


@router.post("/create", response_model=CreateProjectResponse)
async def create_project(
    payload: CreateProjectRequest,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(get_current_user),
) -> CreateProjectResponse:
    require_role(user, [RoleEnum.department_admin, RoleEnum.department_member])

    agent = AgentService(temperature=0.0)
    spec = agent.create_project_spec(payload.instruction)

    # Ensure departments and placeholder users
    primary_department: Optional[Department] = None
    for dept_name in spec.departments or ["General Studies"]:
        dept = db.query(Department).filter(Department.name == dept_name).first()
        if not dept:
            dept = Department(name=dept_name)
            db.add(dept)
            db.flush()
        if primary_department is None:
            primary_department = dept

    project = Project(title=spec.title, summary=spec.summary, department_id=primary_department.id if primary_department else None)
    db.add(project)
    db.flush()

    # Create resources
    for r in spec.resources:
        db.add(Resource(project_id=project.id, name=r.name, type=r.type, url=r.url))

    # Create tasks and placeholder users if needed
    for t in spec.tasks:
        assignee_id: Optional[int] = None
        if t.assignee:
            email = f"{t.assignee.lower().replace(' ', '.')}@example.edu"
            user_obj = db.query(User).filter(User.email == email).first()
            if not user_obj:
                user_obj = User(email=email, name=t.assignee, role=RoleEnum.collaborator, department_id=primary_department.id if primary_department else None)
                db.add(user_obj)
                db.flush()
            assignee_id = user_obj.id
        db.add(Task(project_id=project.id, title=t.title, description=t.description, assignee_id=assignee_id))

    db.commit()
    db.refresh(project)

    # Create CrewAI job
    crew_client = CrewAIClient()
    job_resp = await crew_client.create_job(
        {
            "project_id": project.id,
            "title": project.title,
            "summary": project.summary,
        }
    )
    crew_job = CrewJob(project_id=project.id, external_id=job_resp.id, status=job_resp.status, payload=None)
    db.add(crew_job)
    db.commit()
    db.refresh(project)

    return CreateProjectResponse(project=project, crew_job_id=job_resp.id)


@router.post("/{task_id}/assign")
def assign_task(
    task_id: int,
    payload: AssignTaskRequest,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(get_current_user),
) -> dict:
    require_role(user, [RoleEnum.department_admin, RoleEnum.department_member])
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    assignee = db.query(User).filter(User.id == payload.user_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="User not found")
    task.assignee_id = assignee.id
    db.commit()
    return {"status": "ok"}


