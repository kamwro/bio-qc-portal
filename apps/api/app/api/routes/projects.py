from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_project_service, get_run_service
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.run import RunCreate, RunResponse
from app.services.project import ProjectService
from app.services.run import RunService

router = APIRouter()

ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
RunServiceDep = Annotated[RunService, Depends(get_run_service)]


@router.get("", response_model=list[ProjectResponse])
def list_projects(svc: ProjectServiceDep):
    return svc.list_projects()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, svc: ProjectServiceDep):
    return svc.create_project(body)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, svc: ProjectServiceDep):
    return svc.get_project(project_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, svc: ProjectServiceDep):
    svc.delete_project(project_id)


@router.get("/{project_id}/runs", response_model=list[RunResponse])
def list_runs(project_id: str, svc: RunServiceDep):
    return svc.list_runs(project_id)


@router.post(
    "/{project_id}/runs",
    response_model=RunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_run(project_id: str, body: RunCreate, svc: RunServiceDep):
    return svc.create_run(project_id, body)
