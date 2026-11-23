
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, model_serializer

from app.models.preprocessing_request import DataQualityReport


class PreparedDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    format: Literal["csv", "parquet", "dataframe", "api_payload"]
    location: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None


class FeatureInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    data_type: str
    role: Literal["feature", "target", "identifier", "excluded"]


class TransformationStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: str
    status: Literal[
        "planned",
        "applied",
        "skipped",
        "failed",
        "review_required"
    ]
    parameters: Optional[dict] = None
    affected_columns: list[str]
    message: Optional[str] = None


class PreprocessingWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    severity: Literal["info", "warning", "error"]
    column: Optional[str] = None


class PreprocessingError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    field: Optional[str] = None


class PreprocessingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    status: Literal[
        "success",
        "partial_success",
        "failed",
        "review_required"
    ]
    prepared_dataset: Optional[PreparedDataset] = None
    feature_list: list[FeatureInfo]
    transformation_steps: list[TransformationStep]
    warnings: list[PreprocessingWarning]
    error: Optional[PreprocessingError] = None
    data_quality_reports: Optional[list[DataQualityReport]] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        data = handler(self)
        if data.get("data_quality_reports") is None:
            data.pop("data_quality_reports", None)
        return data
