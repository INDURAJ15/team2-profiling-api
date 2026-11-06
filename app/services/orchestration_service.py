from app.services.profiling_adapter import profile_sample_dataset
from app.services.quality_adapter import check_data_quality


def run_dataset_services(
    dataset_source,
    dataset_id,
    request_id=None,
    dataset_name=None,
    options=None,
    metadata=None,
    target_col=None,
    id_cols=None
):
    options = options or {}
    metadata = metadata or {}

    # Common dataset context for both services
    dataset_context = {
        "dataset_id": dataset_id,
        "dataset_name": dataset_name or dataset_id,
        "source_type": "file"
    }

    # 1. Run Profiling independently
    try:
        profiling_result = profile_sample_dataset(
            dataset_source=dataset_source,
            dataset_id=dataset_id,
            request_id=request_id,
            options=options,
            metadata={
                **metadata,
                "name": dataset_name or dataset_id
            }
        )
    except Exception:
        profiling_result = {
            "status": "failed",
            "errors": [{
                "code": "PROFILING_SERVICE_ERROR",
                "message": "Profiling service execution failed."
            }]
        }

    # 2. Run Data Quality independently
    try:
        quality_result = check_data_quality(
            dataset_source=dataset_source,
            dataset_name=dataset_name or dataset_id,
            target_col=target_col,
            id_cols=id_cols
        )
    except Exception:
        quality_result = {
            "status": "failed",
            "validation_summary": {
                "total_issues_detected": 0,
                "total_duplicate_records": 0,
                "execution_mode": "non_destructive",
                "source_mutated": False
            },
            "issue_logs": [],
            "errors": [{
                "code": "QUALITY_SERVICE_ERROR",
                "message": "Data quality service execution failed."
            }]
        }

    # 3. Determine overall execution status
    profiling_status = profiling_result.get("status", "failed")
    quality_status = quality_result.get("status", "failed")

    failed_count = sum([
        profiling_status == "failed",
        quality_status == "failed"
    ])

    if failed_count == 2:
        overall_status = "failed"
    elif failed_count == 1:
        overall_status = "partial_success"
    elif "warning" in [profiling_status, quality_status]:
        overall_status = "warning"
    else:
        overall_status = "success"

    # 4. Return combined orchestration response
         # 4. Return combined orchestration response
    return {
        "dataset_context": dataset_context,
        "status": overall_status,

        "service_status": {
            "profiling": profiling_status,
            "quality": quality_status,
            "semantic_analysis": "not_configured"
        },

        "downstream_context": {
            "profiling_output_available": profiling_status != "failed",
            "quality_findings_available": quality_status != "failed",
            "semantic_output_available": False,
            "quality_issue_count": quality_result.get(
                "validation_summary", {}
            ).get("total_issues_detected", 0)
        },

        "profiling": profiling_result,
        "quality": quality_result,

        "semantic_analysis": {
            "status": "not_configured",
            "message": (
                "Semantic Analysis service/API contract "
                "is not yet available for integration."
            )
        }
    }
    