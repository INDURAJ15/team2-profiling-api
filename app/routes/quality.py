from fastapi import APIRouter
from pydantic import BaseModel

from app.services.quality_adapter import check_data_quality

router = APIRouter(
    prefix="/api/v1/quality",
    tags=["Data Quality"]
)


class QualityRequest(BaseModel):
    dataset_id: str
    version: str


@router.post("/")
def validate_dataset(request: QualityRequest):

    try:
        result = check_data_quality()

        return {
            "status": "success",
            "message": "Data quality validation completed successfully",
            "dataset_id": request.dataset_id,
            "version": request.version,
            "quality_metadata": result
        }

    except Exception as error:
        return {
            "status": "error",
            "message": "Data quality validation failed",
            "details": str(error)
        }