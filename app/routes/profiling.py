from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.profiling_adapter import profile_sample_dataset

router = APIRouter(
    prefix="/api/v1/profiling",
    tags=["Profiling"]
)


class ProfilingRequest(BaseModel):
    dataset_id: str
    version: str
    include_column_statistics: bool = True
    include_missing_value_counts: bool = True
    sample_limit: Optional[int] = 10000


@router.post("/")
def profile_dataset(request: ProfilingRequest):

    try:
        result = profile_sample_dataset()

        return {
            "status": "success",
            "message": "Dataset profiling completed successfully",
            "dataset_id": request.dataset_id,
            "version": request.version,
            "profiling_metadata": result
        }

    except Exception as error:
        return {
            "status": "error",
            "message": "Dataset profiling failed",
            "details": str(error)
        }