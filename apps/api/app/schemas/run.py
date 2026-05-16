from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RunCreate(BaseModel):
    name: str
    platform: str


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    platform: str
    status: str
    created_at: datetime
