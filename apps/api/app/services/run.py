from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.run import SequencingRun
from app.repositories.project import ProjectRepository
from app.repositories.run import RunRepository
from app.schemas.run import RunCreate


class RunService:
    def __init__(self, db: Session) -> None:
        self.repo = RunRepository(db)
        self.project_repo = ProjectRepository(db)

    def list_runs(self, project_id: str) -> list[type[SequencingRun]]:
        if self.project_repo.get_by_id(project_id) is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return self.repo.get_by_project(project_id)

    def get_run(self, run_id: str) -> type[SequencingRun]:
        run = self.repo.get_by_id(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return run

    def create_run(self, project_id: str, data: RunCreate) -> SequencingRun:
        if self.project_repo.get_by_id(project_id) is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return self.repo.create(
            project_id=project_id, name=data.name, platform=data.platform
        )
