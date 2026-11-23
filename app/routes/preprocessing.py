
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.models.preprocessing_request import PreprocessingRequest
from app.preprocessing.preprocessing_service import preprocess_request
from app.preprocessing.integration_service import run_integrated_preprocessing

router = APIRouter(prefix="/api/v1", tags=["Preprocessing"])

BASE_DIR = Path(__file__).resolve().parents[2]


def validate_dataset_location(request: PreprocessingRequest) -> Path:
    fmt = request.dataset.format

    if fmt not in {"csv", "xlsx", "parquet"}:
        raise HTTPException(
            status_code=400,
            detail="Only CSV, XLSX and Parquet file preprocessing is supported."
        )

    if not request.dataset.location:
        raise HTTPException(
            status_code=400,
            detail="Dataset location is required."
        )

    candidate = Path(request.dataset.location)

    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate

    try:
        candidate = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        raise HTTPException(
            status_code=404,
            detail="Dataset file was not found."
        )

    if not candidate.is_relative_to(BASE_DIR):
        raise HTTPException(
            status_code=403,
            detail="Dataset must be located inside the Team 2 project directory."
        )

    if not candidate.is_file():
        raise HTTPException(
            status_code=404,
            detail="Dataset file was not found."
        )

    if candidate.suffix.lower() != f".{fmt}":
        raise HTTPException(
            status_code=400,
            detail="Dataset format does not match the file extension."
        )

    return candidate


@router.post("/preprocessing/")
def preprocess_dataset(request: PreprocessingRequest):
    dataset_path = validate_dataset_location(request)

    payload = request.model_dump(
        mode="json",
        exclude_none=True
    )

    payload["dataset"]["location"] = str(dataset_path)

    return preprocess_request(payload)


@router.post("/integrated/preprocessing/")
def integrated_preprocessing(request: PreprocessingRequest):
    dataset_path = validate_dataset_location(request)

    payload = request.model_dump(
        mode="json",
        exclude_none=True
    )

    payload["dataset"]["location"] = str(dataset_path)

    return run_integrated_preprocessing(payload)
