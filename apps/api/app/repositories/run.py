from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.run import SequencingRun


class RunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_project(self, project_id: str) -> list[SequencingRun]:
        stmt = (
            select(SequencingRun)
            .where(SequencingRun.project_id == project_id)
            .order_by(SequencingRun.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, run_id: str) -> SequencingRun | None:
        stmt = select(SequencingRun).where(SequencingRun.id == run_id)
        return self.db.scalars(stmt).first()

    def create(self, project_id: str, name: str, platform: str) -> SequencingRun:
        run = SequencingRun(project_id=project_id, name=name, platform=platform)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update_status(self, run_id: str, status: str) -> SequencingRun | None:
        run = self.get_by_id(run_id)
        if run is None:
            return None
        run.status = status
        self.db.commit()
        self.db.refresh(run)
        return run
