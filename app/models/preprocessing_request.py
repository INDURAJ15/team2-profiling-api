
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class DatasetInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    format: Literal[
        "csv", "xlsx", "parquet", "dataframe", "api_payload"
    ]
    location: Optional[str] = None


class PreprocessingOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    handle_missing_values: bool
    encode_categorical: bool
    scale_numeric: bool = False
    extract_date_features: bool = False
    rare_category_threshold: Optional[float] = Field(
        default=None, ge=0, le=1
    )


class QualityRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    column: str
    severity: Literal[
        "LOW", "INFORMATIONAL", "MEDIUM", "BLOCKING"
    ]
    affected_rows: int
    description: str
    recommended_action: str


class DataQualityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    validation_status: Literal[
        "SUCCESS", "SUCCESS_WITH_WARNINGS", "FAILED"
    ]
    total_errors: int
    total_warnings: int
    quality_rules_evaluated: list[QualityRule]


class DataQualityIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issue_id: str
    column: str
    severity: Literal["WARNING", "CRITICAL"]
    affected_count: int
    percentage: float
    description: str


class DataQualityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file: str
    sheet: Optional[str]
    total_rows: int
    total_columns: int
    total_issues_detected: int
    is_source_modified: Literal[False]
    issues: list[DataQualityIssue]


class QualityFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str
    severity: Literal["info", "warning", "error"]
    column: Optional[str] = None
    description: Optional[str] = None


class PreprocessingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    dataset: DatasetInfo
    target: Optional[str]

    problem_type: Literal[
        "classification", "regression", "clustering", "unknown"
    ]

    preprocessing_options: PreprocessingOptions

    data_quality_result: Optional[DataQualityResult] = None
    data_quality_reports: Optional[list[DataQualityReport]] = None
    source_data_preserved: Optional[Literal[True]] = True
    profiling_metadata_received: Optional[bool] = None
    profiling_metadata: Optional[dict] = None
    quality_findings: Optional[list[QualityFinding]] = None
    identifier_columns: Optional[list[str]] = None
