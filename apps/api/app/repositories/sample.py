from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.qc_metric import QCMetric
from app.models.sample import Sample


class SampleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_run(self, run_id: str) -> list[Sample]:
        stmt = (
            select(Sample)
            .options(joinedload(Sample.qc_metric))
            .where(Sample.run_id == run_id)
            .order_by(Sample.sample_name)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, sample_id: str) -> Sample | None:
        stmt = (
            select(Sample)
            .options(joinedload(Sample.qc_metric))
            .where(Sample.id == sample_id)
        )
        return self.db.scalars(stmt).first()

    def create_with_metric(
        self,
        run_id: str,
        sample_name: str,
        external_id: str | None,
        total_reads: int,
        q30_score: float,
        gc_content: float,
        duplication_rate: float,
        adapter_content: float,
        mean_read_quality: float,
        qc_status: str,
    ) -> Sample:
        sample = Sample(run_id=run_id, sample_name=sample_name, external_id=external_id)
        self.db.add(sample)
        self.db.flush()

        metric = QCMetric(
            sample_id=sample.id,
            total_reads=total_reads,
            q30_score=q30_score,
            gc_content=gc_content,
            duplication_rate=duplication_rate,
            adapter_content=adapter_content,
            mean_read_quality=mean_read_quality,
            qc_status=qc_status,
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(sample)
        return sample

    def delete_by_run(self, run_id: str) -> None:
        stmt = select(Sample).where(Sample.run_id == run_id)
        samples = self.db.scalars(stmt).all()
        for s in samples:
            self.db.delete(s)
        self.db.commit()
