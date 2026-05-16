from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sample import Sample
from app.repositories.run import RunRepository
from app.repositories.sample import SampleRepository
from app.schemas.qc_metric import ImportRequest, ImportResponse, QCSummary
from app.schemas.sample import RunReport
from app.services.qc import calculate_qc_status


class SampleService:
    def __init__(self, db: Session) -> None:
        self.repo = SampleRepository(db)
        self.run_repo = RunRepository(db)

    def _get_run_or_404(self, run_id: str):  # type: ignore[return]
        run = self.run_repo.get_by_id(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return run

    def import_samples(self, run_id: str, data: ImportRequest) -> ImportResponse:
        self._get_run_or_404(run_id)

        counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
        for item in data.samples:
            status = calculate_qc_status(
                q30_score=item.q30_score,
                gc_content=item.gc_content,
                duplication_rate=item.duplication_rate,
                adapter_content=item.adapter_content,
            )
            self.repo.create_with_metric(
                run_id=run_id,
                sample_name=item.sample_name,
                external_id=item.external_id,
                total_reads=item.total_reads,
                q30_score=item.q30_score,
                gc_content=item.gc_content,
                duplication_rate=item.duplication_rate,
                adapter_content=item.adapter_content,
                mean_read_quality=item.mean_read_quality,
                qc_status=status,
            )
            counts[status] += 1

        self.run_repo.update_status(run_id, "imported")

        return ImportResponse(
            imported=len(data.samples),
            pass_count=counts["PASS"],
            warn_count=counts["WARN"],
            fail_count=counts["FAIL"],
        )

    def list_samples(self, run_id: str) -> list[type[Sample]]:
        self._get_run_or_404(run_id)
        return self.repo.get_by_run(run_id)

    def get_sample(self, sample_id: str) -> type[Sample]:
        sample = self.repo.get_by_id(sample_id)
        if sample is None:
            raise HTTPException(status_code=404, detail="Sample not found")
        return sample

    def get_qc_summary(self, run_id: str) -> QCSummary:
        self._get_run_or_404(run_id)
        samples = self.repo.get_by_run(run_id)
        metrics = [s.qc_metric for s in samples if s.qc_metric is not None]

        total = len(metrics)
        if total == 0:
            return QCSummary(
                run_id=run_id,
                total_samples=0,
                pass_count=0,
                warn_count=0,
                fail_count=0,
                pass_rate=0.0,
                avg_q30_score=0.0,
                avg_gc_content=0.0,
                avg_duplication_rate=0.0,
            )

        pass_count = sum(1 for m in metrics if m.qc_status == "PASS")
        warn_count = sum(1 for m in metrics if m.qc_status == "WARN")
        fail_count = sum(1 for m in metrics if m.qc_status == "FAIL")

        return QCSummary(
            run_id=run_id,
            total_samples=total,
            pass_count=pass_count,
            warn_count=warn_count,
            fail_count=fail_count,
            pass_rate=round(pass_count / total * 100, 1),
            avg_q30_score=round(sum(m.q30_score for m in metrics) / total, 2),
            avg_gc_content=round(sum(m.gc_content for m in metrics) / total, 2),
            avg_duplication_rate=round(
                sum(m.duplication_rate for m in metrics) / total, 2
            ),
        )

    def get_report(self, run_id: str) -> RunReport:
        run = self._get_run_or_404(run_id)
        summary = self.get_qc_summary(run_id)
        samples = self.repo.get_by_run(run_id)

        worst = sorted(
            [s for s in samples if s.qc_metric is not None],
            key=lambda s: s.qc_metric.adapter_content,  # type: ignore[union-attr]
            reverse=True,
        )[:5]

        return RunReport(
            run_id=run_id,
            run_name=run.name,
            project_id=run.project_id,
            generated_at=datetime.now(tz=UTC),
            total_samples=summary.total_samples,
            pass_count=summary.pass_count,
            warn_count=summary.warn_count,
            fail_count=summary.fail_count,
            avg_q30_score=summary.avg_q30_score,
            avg_gc_content=summary.avg_gc_content,
            avg_duplication_rate=summary.avg_duplication_rate,
            worst_samples_by_adapter_content=[
                {
                    "sample_name": s.sample_name,
                    "adapter_content": s.qc_metric.adapter_content,  # type: ignore[union-attr]
                    "qc_status": s.qc_metric.qc_status,  # type: ignore[union-attr]
                }
                for s in worst
            ],
        )
