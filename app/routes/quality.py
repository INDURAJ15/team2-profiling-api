
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.quality_adapter import check_data_quality

router = APIRouter(
    prefix="/api/v1/quality",
    tags=["Data Quality"]
)


# Approved dataset locations for local integration testing

DATASET_REGISTRY = {
    "hr_department": {
        "path": r"C:\Users\ASUS\Downloads\HumanResources.Department (1).xlsx",
        "name": "Department",
        "id_cols": ["DepartmentID"]
    },
    "hr_employee": {
        "path": r"C:\Users\ASUS\Downloads\HumanResources.Employee.xlsx",
        "name": "Employee",
        "id_cols": ["BusinessEntityID"],
        "target_col": "VacationHours"
    }
}



class QualityRequest(BaseModel):
    dataset_id: str
    version: str


@router.post("/")
def validate_dataset(request: QualityRequest):

    try:
        dataset = DATASET_REGISTRY.get(request.dataset_id)

        if dataset is None:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        result = check_data_quality(
            dataset_source=dataset["path"],
            dataset_name=dataset["name"],
            id_cols=dataset["id_cols"],
            target_col=dataset.get("target_col")
        )

        return {
            "status": "success",
            "message": "Data quality validation completed successfully",
            "dataset_id": request.dataset_id,
            "version": request.version,
            "quality_metadata": {
                "validation_summary": result["validation_summary"],
                "issue_logs": result["issue_logs"]
            }
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Data quality validation failed",
                "details": str(error)
            }
        )
