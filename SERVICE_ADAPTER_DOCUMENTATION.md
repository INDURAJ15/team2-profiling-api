# Team 2 – Profiling and Quality Service Integration

## 1. Project Overview
Team 2 Backend and AI/ML Integration provides APIs for Data Profiling, Data Quality, and Orchestration.

## 2. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Health check |
| POST | /api/v1/profiling/ | Dataset profiling |
| POST | /api/v1/quality/ | Data quality analysis |
| POST | /api/v1/orchestration/ | Combined service execution |

Swagger documentation: http://127.0.0.1:8000/docs

## 3. Profiling Adapter

- Accepts the Team 1 profiling request contract.
- Supports CSV and XLSX dataset sources.
- Generates dataset and column-level statistics.
- Reports missing values, unique values, data types and statistical information.
- Returns warnings and errors using the agreed response structure.
- Supports correlations where configured.

Main response fields:
schema_version, request_id, module, status, generated_at, duration_ms, dataset_reference, dataset, columns, warnings, errors, correlations.

Validation:
HTTP 200 – Team 1 schema validation successful.

## 4. Quality Adapter

- Executes the integrated Data Quality Engine.
- Maps detected findings into quality issue records.
- Reports missing values, duplicate records and statistical outliers where supported.
- Handles missing and empty dataset errors.
- Uses non-destructive execution; source_mutated is False.

Quality endpoint request:
{
  "dataset_id": "hr_department",
  "version": "v1"
}

Response fields:
status, message, dataset_id, version, quality_metadata.

## 5. Orchestration Service

- Executes Profiling and Quality services for a common dataset context.
- Makes profiling and quality outputs available to downstream services.
- Supports partial service failure handling.
- Reports Semantic Analysis as not_configured until its API contract is available.

## 6. Final Integration Test Evidence

- Profiling schema validation: PASS – HTTP 200.
- Quality endpoint: PASS – HTTP 200, status success.
- Orchestration endpoint: PASS – HTTP 200, overall status success.
- Profiling service status: success.
- Quality service status: success.
- Sample quality findings: 3 issues.
- Source mutation: False.
- Demo JSON files saved:
  - demo_outputs/profiling_response.json
  - demo_outputs/quality_response.json
  - demo_outputs/orchestration_response.json

## 7. Known Limitations and Dependencies

1. Semantic Analysis integration is pending. Team/API endpoint and request-response contract are required.
2. Mixed non-numeric values inside numeric columns are reported by Profiling as MIXED_TYPES, but the current Quality Engine does not consistently report them as quality findings.
3. Team 1 confirmation is required for the expected mixed-value validation rule ID, severity and ownership.
4. Invalid date and unusual data-type detection needs further validation.

## 8. Next Sprint Integration Requirements

- Obtain Semantic Analysis API endpoint, request/response schema, authentication and error-handling details.
- Confirm mixed-type validation rules with Team 1.
- Align Quality response contract with the agreed shared schema.
- Add regression tests for invalid dates, mixed values and unusual data types.
- Verify end-to-end execution after Semantic Analysis integration.
- Update integration documentation after contract approval.

## 9. Demonstration

Start the API:
uvicorn main:app --reload

Open:
http://127.0.0.1:8000/docs

Demonstrate Profiling, Quality and Orchestration endpoints using the saved sample datasets and JSON responses.

---
Team: Team 2 – Backend and AI/ML Integration
