from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.repo = ProjectRepository(db)

    def list_projects(self) -> list[Project]:
        return self.repo.get_all()

    def get_project(self, project_id: str) -> Project:
        project = self.repo.get_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def create_project(self, data: ProjectCreate) -> Project:
        return self.repo.create(name=data.name, description=data.description)

    def delete_project(self, project_id: str) -> None:
        deleted = self.repo.delete(project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
