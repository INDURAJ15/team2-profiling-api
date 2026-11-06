from fastapi import APIRouter
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.services.orchestration_service import run_dataset_services

router = APIRouter(
    prefix="/api/v1/orchestration",
    tags=["Orchestration"]
)


class OrchestrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(min_length=1)
    dataset_source: str = Field(min_length=1)
    request_id: Optional[str] = None
    dataset_name: Optional[str] = None
    target_col: Optional[str] = None
    id_cols: list[str] = Field(default_factory=list)
    options: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


@router.post("/")
def orchestrate_dataset(request: OrchestrationRequest):
    return run_dataset_services(
        dataset_source=request.dataset_source,
        dataset_id=request.dataset_id,
        request_id=request.request_id,
        dataset_name=request.dataset_name,
        options=request.options,
        metadata=request.metadata,
        target_col=request.target_col,
        id_cols=request.id_cols or None
    )