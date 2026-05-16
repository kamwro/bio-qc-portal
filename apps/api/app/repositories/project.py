from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[type[Project]]:
        return self.db.query(Project).order_by(Project.created_at.desc()).all()

    def get_by_id(self, project_id: str) -> type[Project] | None:
        return self.db.query(Project).filter(Project.id == project_id).first()

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
