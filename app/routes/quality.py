
from fastapi import APIRouter, HTTPException
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

        quality_metadata = {
            "validation_summary": result["validation_summary"],
            "issue_logs": result["issue_logs"]
        }

        return {
            "status": "success",
            "message": "Data quality validation completed successfully",
            "dataset_id": request.dataset_id,
            "version": request.version,
            "quality_metadata": quality_metadata
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Data quality validation failed",
                "details": str(error)
            }
        )
