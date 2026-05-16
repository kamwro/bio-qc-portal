from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[Project]:
        stmt = select(Project).order_by(Project.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, project_id: str) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        return self.db.scalars(stmt).first()

    def create(self, name: str, description: str | None) -> Project:
        project = Project(name=name, description=description)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: str) -> bool:
        project = self.get_by_id(project_id)
        if project is None:
            return False
        self.db.delete(project)
        self.db.commit()
        return True
