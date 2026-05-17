from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_run_service, get_sample_service
from app.schemas.qc_metric import ImportRequest, ImportResponse, QCSummary
from app.schemas.run import RunResponse
from app.schemas.sample import RunReport, SampleResponse
from app.services.run import RunService
from app.services.sample import SampleService

router = APIRouter()

RunServiceDep = Annotated[RunService, Depends(get_run_service)]
SampleServiceDep = Annotated[SampleService, Depends(get_sample_service)]

ManifestFileDep = Annotated[
    UploadFile,
    File(description="Sample manifest CSV (sample_name, organism, assay_type)"),
]
QCFileDep = Annotated[UploadFile, File(description="QC metrics JSON file")]
QCFormatDep = Annotated[str, Form(description="'simple_json' or 'multiqc_like'")]


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: str, svc: RunServiceDep):
    return svc.get_run(run_id)


@router.post(
    "/{run_id}/import",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
)
def import_samples(run_id: str, body: ImportRequest, svc: SampleServiceDep):
    return svc.import_samples(run_id, body)


@router.post(
    "/{run_id}/import/files",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_samples_from_files(
    run_id: str,
    svc: SampleServiceDep,
    manifest_file: ManifestFileDep,
    qc_file: QCFileDep,
    qc_format: QCFormatDep = "simple_json",
):
    manifest_content = (await manifest_file.read()).decode("utf-8")
    qc_content = (await qc_file.read()).decode("utf-8")
    return svc.import_from_files(run_id, manifest_content, qc_content, qc_format)


@router.get("/{run_id}/samples", response_model=list[SampleResponse])
def list_samples(run_id: str, svc: SampleServiceDep):
    return svc.list_samples(run_id)


@router.get("/{run_id}/qc-summary", response_model=QCSummary)
def qc_summary(run_id: str, svc: SampleServiceDep):
    return svc.get_qc_summary(run_id)


@router.get("/{run_id}/report", response_model=RunReport)
def run_report(run_id: str, svc: SampleServiceDep):
    return svc.get_report(run_id)
