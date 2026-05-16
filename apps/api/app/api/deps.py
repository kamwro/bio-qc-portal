from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.project import ProjectService
from app.services.run import RunService
from app.services.sample import SampleService

SessionDep = Annotated[Session, Depends(get_db)]


def get_project_service(db: SessionDep) -> ProjectService:
    return ProjectService(db)


def get_run_service(db: SessionDep) -> RunService:
    return RunService(db)


def get_sample_service(db: SessionDep) -> SampleService:
    return SampleService(db)
