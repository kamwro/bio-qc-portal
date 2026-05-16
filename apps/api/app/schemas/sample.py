from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.qc_metric import QCMetricResponse


class SampleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    sample_name: str
    external_id: str | None
    created_at: datetime
    qc_metric: QCMetricResponse | None = None


class RunReport(BaseModel):
    run_id: str
    run_name: str
    project_id: str
    generated_at: datetime
    total_samples: int
    pass_count: int
    warn_count: int
    fail_count: int
    avg_q30_score: float
    avg_gc_content: float
    avg_duplication_rate: float
    worst_samples_by_adapter_content: list[dict]
