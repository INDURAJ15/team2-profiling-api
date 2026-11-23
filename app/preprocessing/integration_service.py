"""Integration layer connecting Team 2 profiling and preprocessing."""

from app.services.profiling_adapter import profile_sample_dataset
from app.preprocessing.preprocessing_service import preprocess_request


def run_integrated_preprocessing(request):
    """Run Team 2 profiling first, followed by preprocessing."""

    if not isinstance(request, dict):
        return {
            "status": "failed",
            "profiling": None,
            "preprocessing": None,
            "warnings": [],
            "error": {
                "code": "INVALID_REQUEST",
                "message": "The request must be a JSON object."
            }
        }

    dataset = request.get("dataset", {})
    dataset_id = dataset.get("dataset_id", "")
    location = dataset.get("location", "")
    target = request.get("target")

    profile_options = {
        "include_statistics": True,
        "include_correlations": True
    }

    if target:
        profile_options["target_column"] = target

    profile = profile_sample_dataset(
        dataset_source=location,
        dataset_id=dataset_id,
        request_id=request.get("request_id"),
        options=profile_options,
        metadata={
            "format": dataset.get("format"),
            "name": dataset_id
        }
    )

    if profile.get("status") == "failed":
        return {
            "status": "failed",
            "profiling": profile,
            "preprocessing": None,
            "warnings": [],
            "error": {
                "code": "PROFILING_FAILED",
                "message": "Preprocessing stopped because profiling failed."
            }
        }

    profile_warnings = [
        {
            "code": "PROFILE_" + str(item.get("code", "WARNING")),
            "severity": item.get("severity", "warning"),
            "message": item.get("message", "Profiling warning.")
        }
        for item in profile.get("warnings", [])
    ]

    preprocessing = preprocess_request(request)
    combined_warnings = profile_warnings + preprocessing.get("warnings", [])

    if preprocessing.get("status") == "failed":
        status = "failed"
    elif preprocessing.get("status") == "review_required":
        status = "review_required"
    elif profile.get("status") == "warning" or combined_warnings:
        status = "partial_success"
    else:
        status = "success"

    return {
        "status": status,
        "profiling": profile,
        "preprocessing": preprocessing,
        "warnings": combined_warnings,
        "error": preprocessing.get("error")
    }
