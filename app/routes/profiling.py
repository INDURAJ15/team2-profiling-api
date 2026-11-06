
from fastapi import APIRouter
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal

from app.services.profiling_adapter import profile_sample_dataset

router = APIRouter(
    prefix="/api/v1/profiling",
    tags=["Profiling"]
)


class DatasetReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(min_length=1)
    source_type: Literal["file"] = "file"
    name: Optional[str] = None
    location: str = Field(min_length=1)


class ProfilingMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: Optional[Literal["csv", "xlsx"]] = None
    sheet_name: Optional[str | int] = None
    delimiter: str = ","
    encoding: str = "utf-8"
    missing_value_markers: list[str] = Field(default_factory=list)
    identifier_columns: list[str] = Field(default_factory=list)


class ProfilingOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_n_values: int = Field(default=5, ge=1, le=50)
    include_statistics: bool = True
    target_column: Optional[str] = None
    include_correlations: bool = True


class ProfilingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0-draft"] = "1.0-draft"
    request_id: str = Field(min_length=1)
    dataset_reference: DatasetReference
    metadata: Optional[ProfilingMetadata] = None
    options: Optional[ProfilingOptions] = None


@router.post("/")
def profile_dataset(request: ProfilingRequest):
    return profile_sample_dataset(
        dataset_source=request.dataset_reference.location,
        dataset_id=request.dataset_reference.dataset_id,
        request_id=request.request_id,
        options=request.options.model_dump() if request.options else {},
        metadata={
            **(request.metadata.model_dump() if request.metadata else {}),
            "name": request.dataset_reference.name
        }
    )
