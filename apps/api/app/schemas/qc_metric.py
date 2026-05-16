from pydantic import BaseModel, ConfigDict, Field


class QCMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sample_id: str
    total_reads: int
    q30_score: float
    gc_content: float
    duplication_rate: float
    adapter_content: float
    mean_read_quality: float
    qc_status: str


class SampleImportItem(BaseModel):
    sample_name: str
    external_id: str | None = None
    total_reads: int = Field(gt=0)
    q30_score: float = Field(ge=0, le=100)
    gc_content: float = Field(ge=0, le=100)
    duplication_rate: float = Field(ge=0, le=100)
    adapter_content: float = Field(ge=0, le=100)
    mean_read_quality: float = Field(ge=0)


class ImportRequest(BaseModel):
    samples: list[SampleImportItem]


class ImportResponse(BaseModel):
    imported: int
    pass_count: int
    warn_count: int
    fail_count: int


class QCSummary(BaseModel):
    run_id: str
    total_samples: int
    pass_count: int
    warn_count: int
    fail_count: int
    pass_rate: float
    avg_q30_score: float
    avg_gc_content: float
    avg_duplication_rate: float


class WorstSample(BaseModel):
    sample_name: str
    adapter_content: float
    qc_status: str
