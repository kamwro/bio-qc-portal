from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_sample_service
from app.schemas.sample import SampleResponse
from app.services.sample import SampleService

router = APIRouter()

SampleServiceDep = Annotated[SampleService, Depends(get_sample_service)]


@router.get("/{sample_id}", response_model=SampleResponse)
def get_sample(sample_id: str, svc: SampleServiceDep):
    return svc.get_sample(sample_id)
