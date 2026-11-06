# Team 2 - Data Profiling and Data Quality API Contract

Owner: Team 2 - Backend and AI/ML Integration

## 1. Data Profiling API

Method: POST
Endpoint: /api/v1/profiling/

Request fields:
- schema_version
- request_id
- dataset_reference
- metadata (optional)
- options (optional)

Response fields:
- schema_version
- request_id
- module
- status
- generated_at
- duration_ms
- dataset_reference
- dataset
- columns
- warnings
- errors
- correlations

## 2. Data Quality API

Method: POST
Endpoint: /api/v1/quality/

Request:
{
  "dataset_id": "hr_department",
  "version": "v1"
}

Response fields:
- status
- message
- dataset_id
- version
- quality_metadata
  - validation_summary
  - issue_logs
  - errors

## 3. Orchestration API

Method: POST
Endpoint: /api/v1/orchestration/

Request fields:
- dataset_id
- dataset_source
- request_id (optional)
- dataset_name (optional)
- target_col (optional)
- id_cols
- options
- metadata

Response fields:
- dataset_context
- status
- service_status
- downstream_context
- profiling
- quality
- semantic_analysis

Semantic analysis is currently not configured.

## 4. Health Check

Method: GET
Endpoint: /health

## 5. Integration Notes

- Profiling follows Team 1 contract version 1.0-draft.
- Final approval from Team 1 is pending.
- Quality API uses registered dataset IDs and versions.
- Profiling uses a dataset file location.
- Shared storage or deployment paths must be agreed for cross-team integration.
- Quality testing confirmed non-destructive execution.
- Swagger documentation: http://127.0.0.1:8000/docs

## 6. Test Evidence

- Profiling validation: python validate_profiling.py
- Profiling HTTP status: 200
- Quality API tested with sample and HR datasets.
- Orchestration tested with profiling and quality services.

## 7. GitHub Repository

https://github.com/INDURAJ15/team2-profiling-api
